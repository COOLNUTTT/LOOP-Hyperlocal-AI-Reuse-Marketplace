// Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.

/**
 * On-Device Auto-Detection Engine for LOOP Privacy Scrubber
 *
 * Runs 100% client-side in the browser before any photo leaves the device:
 *  1. Real Face Detection via OpenCV Zoo YuNet ONNX (`models/face_detection_yunet.onnx`, MIT)
 *     executed on `onnxruntime-web` WASM (single-threaded, no COOP/COEP required).
 *  2. Real Text PII Detection (Indian phone numbers, vehicle number plates, IDs/PRNs,
 *     Aadhaar/PAN, and address/PINs) via `tesseract.js` (Apache-2.0) OCR word bounding boxes.
 */
(function (global) {
  "use strict";

  const ORT_CDN = "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.20.1/dist/ort.min.js";
  const ORT_WASM_PREFIX = "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.20.1/dist/";
  const TESSERACT_CDN = "https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js";
  const YUNET_MODEL_URL = "models/face_detection_yunet.onnx";

  const scriptPromises = {};
  let yunetSessionPromise = null;
  let tesseractWorkerPromise = null;

  function loadScriptOnce(url, globalCheck) {
    if (globalCheck()) {
      return Promise.resolve();
    }
    if (scriptPromises[url]) {
      return scriptPromises[url];
    }
    scriptPromises[url] = new Promise((resolve, reject) => {
      if (typeof document === "undefined") {
        reject(new Error("DOM unavailable"));
        return;
      }
      const script = document.createElement("script");
      script.src = url;
      script.async = true;
      script.crossOrigin = "anonymous";
      script.onload = () => resolve();
      script.onerror = () => {
        delete scriptPromises[url];
        reject(new Error(`Failed to load ${url}`));
      };
      document.head.appendChild(script);
    });
    return scriptPromises[url];
  }

  async function getYuNetSession() {
    if (yunetSessionPromise) return yunetSessionPromise;

    yunetSessionPromise = (async () => {
      await loadScriptOnce(ORT_CDN, () => Boolean(global.ort && global.ort.InferenceSession));
      const ort = global.ort;
      ort.env.wasm.wasmPaths = ORT_WASM_PREFIX;
      ort.env.wasm.numThreads = 1;

      const resp = await fetch(YUNET_MODEL_URL);
      if (!resp.ok) {
        throw new Error(`Unable to fetch ${YUNET_MODEL_URL} (HTTP ${resp.status})`);
      }
      const modelBytes = new Uint8Array(await resp.arrayBuffer());
      return ort.InferenceSession.create(modelBytes, {
        executionProviders: ["wasm"],
      });
    })().catch((err) => {
      yunetSessionPromise = null;
      throw err;
    });

    return yunetSessionPromise;
  }

  async function getTesseractWorker() {
    if (tesseractWorkerPromise) return tesseractWorkerPromise;

    tesseractWorkerPromise = (async () => {
      await loadScriptOnce(TESSERACT_CDN, () => Boolean(global.Tesseract && global.Tesseract.createWorker));
      const worker = await global.Tesseract.createWorker("eng");
      return worker;
    })().catch((err) => {
      tesseractWorkerPromise = null;
      throw err;
    });

    return tesseractWorkerPromise;
  }

  function computeIoU(a, b) {
    const x1 = Math.max(a.x, b.x);
    const y1 = Math.max(a.y, b.y);
    const x2 = Math.min(a.x + a.w, b.x + b.w);
    const y2 = Math.min(a.y + a.h, b.y + b.h);
    const interW = Math.max(0, x2 - x1);
    const interH = Math.max(0, y2 - y1);
    const interArea = interW * interH;
    const unionArea = a.w * a.h + b.w * b.h - interArea;
    return unionArea > 0 ? interArea / unionArea : 0;
  }

  function applyNMS(boxes, iouThreshold) {
    const sorted = [...boxes].sort((a, b) => b.confidence - a.confidence);
    const kept = [];
    for (const candidate of sorted) {
      let suppressed = false;
      for (const prev of kept) {
        if (computeIoU(candidate, prev) > iouThreshold) {
          suppressed = true;
          break;
        }
      }
      if (!suppressed) kept.push(candidate);
    }
    return kept;
  }

  function clampNormalizedBox(x, y, w, h, padFrac) {
    const px = w * padFrac;
    const py = h * padFrac;
    const nx = Math.max(0, Math.min(0.98, x - px));
    const ny = Math.max(0, Math.min(0.98, y - py));
    const nw = Math.max(0.02, Math.min(1 - nx, w + px * 2));
    const nh = Math.max(0.02, Math.min(1 - ny, h + py * 2));
    return { x: nx, y: ny, w: nw, h: nh };
  }

  /**
   * Run OpenCV Zoo YuNet (`face_detection_yunet.onnx`) on a raw HTMLCanvasElement.
   */
  async function detectFacesYuNet(sourceCanvas, confThreshold = 0.52) {
    const sw = sourceCanvas.width;
    const sh = sourceCanvas.height;
    if (!sw || !sh) return { boxes: [], engine: "none" };

    // face_detection_yunet_2023mar.onnx expects [1, 3, 640, 640] (or matching inputMetadata)
    const targetSize = 640;
    const scale = Math.min(targetSize / sw, targetSize / sh);
    const rw = Math.max(1, Math.round(sw * scale));
    const rh = Math.max(1, Math.round(sh * scale));

    const prepCanvas = document.createElement("canvas");
    prepCanvas.width = targetSize;
    prepCanvas.height = targetSize;
    const prepCtx = prepCanvas.getContext("2d");
    if (!prepCtx) return { boxes: [], engine: "none" };

    prepCtx.fillStyle = "#000000";
    prepCtx.fillRect(0, 0, targetSize, targetSize);
    prepCtx.drawImage(sourceCanvas, 0, 0, sw, sh, 0, 0, rw, rh);

    try {
      const session = await getYuNetSession();
      const ort = global.ort;
      const imgData = prepCtx.getImageData(0, 0, targetSize, targetSize).data;

      // YuNet expects NCHW BGR float32 in range [0..255]
      const hw = targetSize * targetSize;
      const inputData = new Float32Array(3 * hw);
      for (let i = 0; i < hw; i++) {
        const p = i * 4;
        inputData[i] = imgData[p + 2]; // B
        inputData[hw + i] = imgData[p + 1]; // G
        inputData[2 * hw + i] = imgData[p]; // R
      }

      const inputTensor = new ort.Tensor("float32", inputData, [1, 3, targetSize, targetSize]);
      const outputs = await session.run({ input: inputTensor });

      const rawCandidates = [];
      const strides = [8, 16, 32];

      for (const stride of strides) {
        const clsTensor = outputs[`cls_${stride}`];
        const objTensor = outputs[`obj_${stride}`];
        const bboxTensor = outputs[`bbox_${stride}`];
        if (!clsTensor || !objTensor || !bboxTensor) continue;

        const cls = clsTensor.data;
        const obj = objTensor.data;
        const bbox = bboxTensor.data;
        const cols = Math.floor(targetSize / stride);
        const rows = Math.floor(targetSize / stride);

        for (let r = 0; r < rows; r++) {
          for (let c = 0; c < cols; c++) {
            const idx = r * cols + c;
            const clsScore = Math.max(0, Math.min(1, cls[idx]));
            const objScore = Math.max(0, Math.min(1, obj[idx]));
            const score = Math.sqrt(clsScore * objScore);
            if (score < confThreshold) continue;

            const cx = (c + bbox[idx * 4 + 0]) * stride;
            const cy = (r + bbox[idx * 4 + 1]) * stride;
            const bw = Math.exp(bbox[idx * 4 + 2]) * stride;
            const bh = Math.exp(bbox[idx * 4 + 3]) * stride;

            const x1 = (cx - bw / 2) / scale;
            const y1 = (cy - bh / 2) / scale;
            const origW = bw / scale;
            const origH = bh / scale;

            const normX = Math.max(0, Math.min(1, x1 / sw));
            const normY = Math.max(0, Math.min(1, y1 / sh));
            const normW = Math.max(0.01, Math.min(1 - normX, origW / sw));
            const normH = Math.max(0.01, Math.min(1 - normY, origH / sh));

            if (normW * sw < 8 || normH * sh < 8) continue;

            const padded = clampNormalizedBox(normX, normY, normW, normH, 0.08);
            rawCandidates.push({
              x: padded.x,
              y: padded.y,
              w: padded.w,
              h: padded.h,
              type: "face",
              label: "Face",
              confidence: Math.round(score * 1000) / 1000,
              source: "auto",
            });
          }
        }
      }

      const finalFaces = applyNMS(rawCandidates, 0.35).map((b, i) => ({
        ...b,
        id: `auto-face-${i + 1}`,
      }));
      return { boxes: finalFaces, engine: "yunet-onnx-wasm" };
    } catch (ortErr) {
      // Fallback to native browser FaceDetector if available
      if (typeof global.FaceDetector === "function") {
        try {
          const detector = new global.FaceDetector({ fastMode: true, maxDetectedFaces: 10 });
          const faces = await detector.detect(sourceCanvas);
          const boxes = faces.map((f, i) => {
            const box = f.boundingBox;
            const padded = clampNormalizedBox(
              box.x / sw,
              box.y / sh,
              box.width / sw,
              box.height / sh,
              0.08
            );
            return {
              id: `auto-face-${i + 1}`,
              ...padded,
              type: "face",
              label: "Face",
              confidence: 0.9,
              source: "auto",
            };
          });
          return { boxes, engine: "browser-facedetector" };
        } catch (_) {}
      }
      return { boxes: [], engine: `yunet-unavailable (${ortErr.message})` };
    }
  }

  const PII_TEXT_RULES = [
    {
      type: "phone",
      label: "Phone",
      regex: /(?:(?:\+?91|0)[\s.-]?)?[6-9]\d{4}[\s.-]?\d{5}|(?:\+?91|0)[\s.-]?[6-9]\d{2,4}[\s.-]?\d{3,4}[\s.-]?\d{3,4}/g,
    },
    {
      type: "plate",
      label: "Plate",
      regex: /\b[A-Z]{2}[\s-]?\d{1,2}[\s-]?[A-Z]{1,3}[\s-]?\d{4}\b/gi,
    },
    {
      type: "id_card",
      label: "ID Card",
      regex: /\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b|\b[A-Z]{5}\d{4}[A-Z]\b|\b(?:STUDENT\s*ID|ADYPU\s*STUDENT(?:\s*ID)?|ID|PRN|ROLL\s*(?:NO)?|REG(?:ISTRATION)?)\s*[:#-]?\s*[A-Z0-9-]{2,}\b/gi,
    },
    {
      type: "address",
      label: "Address / PIN",
      regex: /\b(?:flat|hostel|room|block|nagar|road|sector|colony|lane|pin|adypu|pune|lohegaon|viman|wakad|kharadi)\b[^.\n]{0,40}\b[1-9]\d{5}\b|\b(?:flat|hostel|room|block)\s*(?:no\.?|#)?\s*[A-Z0-9-]{1,8}\b/gi,
    },
  ];

  function unionMatchingWordsBox(line, matchStart, matchEnd, ocrW, ocrH) {
    const words = Array.isArray(line.words) ? line.words : [];
    if (!words.length) {
      const b = line.bbox;
      return clampNormalizedBox(
        b.x0 / ocrW,
        b.y0 / ocrH,
        (b.x1 - b.x0) / ocrW,
        (b.y1 - b.y0) / ocrH,
        0.12
      );
    }

    let cursor = 0;
    const rawLine = String(line.text || "");
    let x0 = Infinity;
    let y0 = Infinity;
    let x1 = -Infinity;
    let y1 = -Infinity;
    let matchedAny = false;

    for (const w of words) {
      const wText = String(w.text || "").trim();
      if (!wText) continue;
      const foundIdx = rawLine.indexOf(wText, cursor);
      const wStart = foundIdx !== -1 ? foundIdx : cursor;
      const wEnd = wStart + wText.length;
      cursor = wEnd;

      if (wEnd > matchStart && wStart < matchEnd && w.bbox) {
        x0 = Math.min(x0, w.bbox.x0);
        y0 = Math.min(y0, w.bbox.y0);
        x1 = Math.max(x1, w.bbox.x1);
        y1 = Math.max(y1, w.bbox.y1);
        matchedAny = true;
      }
    }

    if (!matchedAny && line.bbox) {
      x0 = line.bbox.x0;
      y0 = line.bbox.y0;
      x1 = line.bbox.x1;
      y1 = line.bbox.y1;
    }

    if (!Number.isFinite(x0) || !Number.isFinite(x1) || x1 <= x0 || y1 <= y0) {
      return null;
    }

    const padX = Math.max(0.015, ((x1 - x0) / ocrW) * 0.14);
    const padY = Math.max(0.015, ((y1 - y0) / ocrH) * 0.22);
    const nx = Math.max(0, x0 / ocrW - padX);
    const ny = Math.max(0, y0 / ocrH - padY);
    const nw = Math.min(1 - nx, (x1 - x0) / ocrW + padX * 2);
    const nh = Math.min(1 - ny, (y1 - y0) / ocrH + padY * 2);
    return { x: nx, y: ny, w: nw, h: nh };
  }

  /**
   * Run Tesseract.js OCR on a raw HTMLCanvasElement and detect PII text regions.
   */
  async function detectPiiOcr(sourceCanvas, timeoutMs = 12000) {
    const sw = sourceCanvas.width;
    const sh = sourceCanvas.height;
    if (!sw || !sh) return { boxes: [], engine: "none" };

    // Scale to a sweet spot for OCR accuracy & latency (800px..1200px max side)
    const maxDim = Math.max(sw, sh);
    const scale = maxDim < 700 ? 900 / maxDim : maxDim > 1280 ? 1280 / maxDim : 1;
    const ocrW = Math.max(1, Math.round(sw * scale));
    const ocrH = Math.max(1, Math.round(sh * scale));

    const ocrCanvas = document.createElement("canvas");
    ocrCanvas.width = ocrW;
    ocrCanvas.height = ocrH;
    const ocrCtx = ocrCanvas.getContext("2d");
    if (!ocrCtx) return { boxes: [], engine: "none" };
    ocrCtx.drawImage(sourceCanvas, 0, 0, sw, sh, 0, 0, ocrW, ocrH);

    try {
      const worker = await getTesseractWorker();
      const ocrPromise = worker.recognize(ocrCanvas);
      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error("OCR timeout")), timeoutMs)
      );
      const result = await Promise.race([ocrPromise, timeoutPromise]);
      const lines = (result && result.data && result.data.lines) || [];

      const detected = [];
      let countByType = { phone: 0, plate: 0, id_card: 0, address: 0 };

      for (const line of lines) {
        const lineText = String(line.text || "").trim();
        if (!lineText) continue;

        for (const rule of PII_TEXT_RULES) {
          rule.regex.lastIndex = 0;
          let match;
          while ((match = rule.regex.exec(lineText)) !== null) {
            const matchedText = match[0].trim();
            const box = unionMatchingWordsBox(
              line,
              match.index,
              match.index + match[0].length,
              ocrW,
              ocrH
            );
            if (!box) continue;

            countByType[rule.type] = (countByType[rule.type] || 0) + 1;
            detected.push({
              id: `auto-${rule.type}-${countByType[rule.type]}`,
              x: box.x,
              y: box.y,
              w: box.w,
              h: box.h,
              type: rule.type,
              label: rule.label,
              matchedText: matchedText.slice(0, 24),
              confidence: Math.round(Math.max(0.65, (line.confidence || 80) / 100) * 1000) / 1000,
              source: "auto",
            });
          }
        }
      }

      return { boxes: detected, engine: "tesseract-ocr-wasm" };
    } catch (err) {
      return { boxes: [], engine: `ocr-unavailable (${err.message})` };
    }
  }

  function mergeBoxes(boxes) {
    const merged = [];
    for (const box of boxes) {
      const duplicate = merged.find(
        (m) => m.type === box.type && computeIoU(m, box) > 0.45
      );
      if (!duplicate) {
        merged.push(box);
      }
    }
    return merged;
  }

  /**
   * Run Face Detection (YuNet ONNX) + Text PII Detection (Tesseract OCR) in parallel.
   */
  async function detectAll(sourceCanvas, options = {}) {
    const t0 = typeof performance !== "undefined" ? performance.now() : Date.now();

    const [faceRes, ocrRes] = await Promise.all([
      detectFacesYuNet(sourceCanvas, options.faceThreshold || 0.52),
      detectPiiOcr(sourceCanvas, options.ocrTimeoutMs || 12000),
    ]);

    const combined = mergeBoxes([...(faceRes.boxes || []), ...(ocrRes.boxes || [])]);
    const t1 = typeof performance !== "undefined" ? performance.now() : Date.now();

    return {
      boxes: combined,
      faceCount: (faceRes.boxes || []).length,
      textPiiCount: (ocrRes.boxes || []).length,
      latencyMs: Math.max(1, Math.round(t1 - t0)),
      engines: {
        face: faceRes.engine,
        ocr: ocrRes.engine,
      },
    };
  }

  global.LOOPScrubberAutoDetect = {
    detectAll,
    detectFacesYuNet,
    detectPiiOcr,
  };
})(typeof window !== "undefined" ? window : globalThis);
