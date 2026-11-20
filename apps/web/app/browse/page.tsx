// Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"use client";

import React, { useState, useMemo } from "react";
import Link from "next/link";
import {
  Search,
  Filter,
  MapPin,
  Grid,
  Map as MapIcon,
  Sparkles,
  SlidersHorizontal,
  X,
  Layers,
  Tag,
  ArrowUpDown,
} from "lucide-react";
import FairDealBadge from "@/components/FairDealBadge";

// Initial realistic demo items aligned with scripts/seed.py
const INITIAL_LISTINGS = [
  {
    id: "demo-listing-1",
    type: "sell",
    category: "electronics",
    subtype: "Calculator",
    brand: "Casio",
    model: "fx-991EX ClassWiz",
    title: "Casio fx-991EX ClassWiz Engineering Calculator",
    description: "Used in engineering mathematics for 2 semesters. Clean solar panel, pristine display.",
    condition: "good",
    price_ask: 850,
    price_likely: 850,
    fair_deal: "fair",
    area_name: "Lohegaon / Charholi",
    geohash5: "tek3x",
    image_url: "/placeholder-calc.jpg",
    views: 42,
  },
  {
    id: "demo-listing-2",
    type: "sell",
    category: "furniture",
    subtype: "Study Table",
    brand: "IKEA",
    model: "Micke Desk",
    title: "IKEA Micke Compact Study Table with Cable Outlet",
    description: "White compact table with drawer. Ideal for student hostel rooms and compact apartments.",
    condition: "like_new",
    price_ask: 2400,
    price_likely: 2800,
    fair_deal: "great",
    area_name: "Wakad / Hinjawadi",
    geohash5: "tek30",
    image_url: "/placeholder-desk.jpg",
    views: 89,
  },
  {
    id: "demo-listing-3",
    type: "donate",
    category: "books",
    subtype: "Textbook",
    brand: "Pearson",
    model: "44th Edition",
    title: "Higher Engineering Mathematics by B.S. Grewal",
    description: "Complete textbook for Sem 1 & 2 engineering. Clean pages, binding intact.",
    condition: "good",
    price_ask: 0,
    price_likely: 250,
    fair_deal: "great",
    area_name: "Lohegaon",
    geohash5: "tek3x",
    image_url: "/placeholder-book.jpg",
    views: 120,
  },
  {
    id: "demo-listing-4",
    type: "swap",
    category: "hobbies",
    subtype: "Acoustic Guitar",
    brand: "Yamaha",
    model: "F280",
    title: "Yamaha F280 Acoustic Guitar with Gig Bag",
    description: "Warm acoustic tone with smooth action. Looking to swap for a USB audio interface or desktop monitor.",
    condition: "like_new",
    price_ask: 5200,
    price_likely: 5200,
    fair_deal: "fair",
    area_name: "Viman Nagar",
    geohash5: "tek3y",
    image_url: "/placeholder-guitar.jpg",
    views: 65,
  },
];

// Area centroids for coarse map visualization (Zero exact addresses)
const COARSE_AREAS = [
  { name: "Lohegaon / Charholi", geohash5: "tek3x", count: 2, lat: 18.601, lng: 73.916 },
  { name: "Wakad / Hinjawadi", geohash5: "tek30", count: 1, lat: 18.598, lng: 73.762 },
  { name: "Viman Nagar", geohash5: "tek3y", count: 1, lat: 18.567, lng: 73.914 },
];

export default function BrowsePage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [selectedType, setSelectedType] = useState<string>("all");
  const [selectedCondition, setSelectedCondition] = useState<string>("all");
  const [maxPrice, setMaxPrice] = useState<number>(10000);
  const [selectedArea, setSelectedArea] = useState<string>("all");
  const [viewMode, setViewMode] = useState<"grid" | "map">("grid");
  const [showMobileFilters, setShowMobileFilters] = useState(false);

  const filteredListings = useMemo(() => {
    return INITIAL_LISTINGS.filter((item) => {
      if (selectedCategory !== "all" && item.category !== selectedCategory) return false;
      if (selectedType !== "all" && item.type !== selectedType) return false;
      if (selectedCondition !== "all" && item.condition !== selectedCondition) return false;
      if (selectedArea !== "all" && item.area_name !== selectedArea) return false;
      if (item.price_ask > maxPrice) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matches =
          item.title.toLowerCase().includes(q) ||
          item.description.toLowerCase().includes(q) ||
          item.brand.toLowerCase().includes(q) ||
          item.subtype.toLowerCase().includes(q);
        if (!matches) return false;
      }
      return true;
    });
  }, [searchQuery, selectedCategory, selectedType, selectedCondition, maxPrice, selectedArea]);

  return (
    <div className="space-y-6">
      {/* Top Search & Filter Bar */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative flex-1">
          <input
            type="text"
            placeholder="Search items, textbooks, calculators, furniture..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-xl border border-slate-300 bg-white py-2.5 pl-10 pr-4 text-sm text-slate-900 placeholder-slate-400 focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900 shadow-sm"
          />
          <Search className="pointer-events-none absolute left-3 top-3 h-4 w-4 text-slate-400" />
        </div>

        <div className="flex items-center gap-2">
          {/* Mobile Filter Toggle */}
          <button
            onClick={() => setShowMobileFilters(true)}
            className="flex sm:hidden items-center gap-1.5 rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-xs font-semibold text-slate-700 shadow-sm"
          >
            <Filter className="h-4 w-4" />
            <span>Filters</span>
          </button>

          {/* View Mode Toggle */}
          <div className="flex rounded-xl border border-slate-200 bg-white p-1 shadow-sm">
            <button
              onClick={() => setViewMode("grid")}
              className={`flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors ${
                viewMode === "grid" ? "bg-slate-900 text-white" : "text-slate-600 hover:text-slate-900"
              }`}
            >
              <Grid className="h-3.5 w-3.5" />
              <span>Grid</span>
            </button>
            <button
              onClick={() => setViewMode("map")}
              className={`flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors ${
                viewMode === "map" ? "bg-slate-900 text-white" : "text-slate-600 hover:text-slate-900"
              }`}
            >
              <MapIcon className="h-3.5 w-3.5" />
              <span>Coarse Map</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-4">
        {/* Desktop Sidebar Filters */}
        <aside className="hidden lg:block space-y-6 rounded-xl border border-slate-200 bg-white p-5 shadow-sm h-fit">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h2 className="text-sm font-bold text-slate-900">Filters</h2>
            <button
              onClick={() => {
                setSelectedCategory("all");
                setSelectedType("all");
                setSelectedCondition("all");
                setMaxPrice(10000);
                setSelectedArea("all");
                setSearchQuery("");
              }}
              className="text-xs font-medium text-slate-500 hover:text-slate-900"
            >
              Reset
            </button>
          </div>

          {/* Category */}
          <div className="space-y-2">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-700">Category</label>
            <div className="space-y-1">
              {["all", "electronics", "furniture", "books", "hobbies"].map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`block w-full text-left rounded-lg px-2.5 py-1.5 text-xs font-medium capitalize transition-colors ${
                    selectedCategory === cat ? "bg-slate-900 text-white font-semibold" : "text-slate-600 hover:bg-slate-50"
                  }`}
                >
                  {cat === "all" ? "All Categories" : cat}
                </button>
              ))}
            </div>
          </div>

          {/* Listing Type */}
          <div className="space-y-2">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-700">Trade Type</label>
            <div className="grid grid-cols-3 gap-1">
              {["all", "sell", "donate", "swap"].map((t) => (
                <button
                  key={t}
                  onClick={() => setSelectedType(t)}
                  className={`rounded-lg py-1.5 text-[11px] font-semibold uppercase transition-colors ${
                    selectedType === t ? "bg-slate-900 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {/* Price Ceiling */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <label className="font-semibold uppercase tracking-wider text-slate-700">Max Price</label>
              <span className="font-bold text-slate-900">₹{maxPrice}</span>
            </div>
            <input
              type="range"
              min="0"
              max="10000"
              step="100"
              value={maxPrice}
              onChange={(e) => setMaxPrice(Number(e.target.value))}
              className="w-full accent-slate-900"
            />
          </div>

          {/* Coarse Locality */}
          <div className="space-y-2">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-700">Coarse Locality</label>
            <select
              value={selectedArea}
              onChange={(e) => setSelectedArea(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white px-2.5 py-1.5 text-xs text-slate-900 focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
            >
              <option value="all">All Pune Localities</option>
              <option value="Lohegaon / Charholi">Lohegaon / Charholi (ADYPU)</option>
              <option value="Wakad / Hinjawadi">Wakad / Hinjawadi</option>
              <option value="Viman Nagar">Viman Nagar</option>
            </select>
          </div>
        </aside>

        {/* Results Area */}
        <div className="lg:col-span-3 space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>
              Showing <strong className="text-slate-900">{filteredListings.length}</strong> items
            </span>
            <span className="bg-slate-100 px-2.5 py-1 rounded-full font-medium">
              Coarse Privacy Guaranteed
            </span>
          </div>

          {/* Grid View */}
          {viewMode === "grid" && (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {filteredListings.map((item) => (
                <Link
                  key={item.id}
                  href={`/listings/${item.id}`}
                  className="group flex flex-col justify-between rounded-xl border border-slate-200 bg-white p-4 shadow-sm hover:border-slate-300 hover:shadow-md transition-all"
                >
                  <div className="space-y-3">
                    <div className="relative h-40 w-full overflow-hidden rounded-lg bg-slate-100 flex items-center justify-center">
                      <div className="text-center p-3">
                        <Tag className="mx-auto h-8 w-8 text-slate-400 group-hover:scale-110 transition-transform" />
                        <span className="mt-1 block text-xs font-semibold text-slate-500 uppercase tracking-wider">
                          {item.category}
                        </span>
                      </div>
                      <span className="absolute top-2 left-2 rounded-full bg-slate-900/80 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-white backdrop-blur">
                        {item.type}
                      </span>
                    </div>

                    <div>
                      <div className="flex items-center justify-between">
                        <h3 className="font-bold text-slate-900 text-sm line-clamp-1 group-hover:text-emerald-700 transition-colors">
                          {item.title}
                        </h3>
                      </div>
                      <p className="mt-1 text-xs text-slate-500 line-clamp-2">{item.description}</p>
                    </div>
                  </div>

                  <div className="mt-4 border-t border-slate-100 pt-3 space-y-2">
                    <div className="flex items-center justify-between">
                      <div>
                        {item.type === "donate" ? (
                          <span className="text-sm font-bold text-emerald-700">Free Donation</span>
                        ) : (
                          <div className="flex items-baseline gap-1">
                            <span className="text-base font-extrabold text-slate-900">₹{item.price_ask}</span>
                          </div>
                        )}
                      </div>
                      <FairDealBadge grade={item.fair_deal} />
                    </div>

                    <div className="flex items-center justify-between text-[11px] text-slate-500">
                      <div className="flex items-center gap-1">
                        <MapPin className="h-3 w-3 text-slate-400" />
                        <span>{item.area_name}</span>
                      </div>
                      <span className="capitalize">{item.condition.replace("_", " ")}</span>
                    </div>
                  </div>
                </Link>
              ))}

              {filteredListings.length === 0 && (
                <div className="col-span-full rounded-xl border border-dashed border-slate-200 bg-white p-8 text-center">
                  <p className="text-sm font-semibold text-slate-700">No matching listings found.</p>
                  <p className="mt-1 text-xs text-slate-500">Try loosening your search filters or price ceiling.</p>
                </div>
              )}
            </div>
          )}

          {/* Coarse Map View */}
          {viewMode === "map" && (
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-slate-900">Neighbourhood Cluster Map</h3>
                  <p className="text-xs text-slate-500">
                    Pins represent approximate ~5km² zones. No exact street addresses are ever broadcast.
                  </p>
                </div>
                <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-800 border border-emerald-200">
                  PostGIS Coarse Clustering
                </span>
              </div>

              {/* Visual Coarse Map Area */}
              <div className="relative h-80 w-full overflow-hidden rounded-xl bg-slate-900 flex items-center justify-center p-4">
                <div className="absolute inset-0 bg-[radial-gradient(#334155_1px,transparent_1px)] [background-size:16px_16px] opacity-40" />

                <div className="relative z-10 grid w-full max-w-lg grid-cols-1 gap-3 sm:grid-cols-3">
                  {COARSE_AREAS.map((area) => (
                    <div
                      key={area.name}
                      onClick={() => setSelectedArea(area.name)}
                      className="cursor-pointer rounded-xl border border-slate-700 bg-slate-800/90 p-3.5 backdrop-blur hover:border-emerald-500 transition-all text-center"
                    >
                      <div className="mx-auto flex h-9 w-9 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400">
                        <MapPin className="h-5 w-5" />
                      </div>
                      <h4 className="mt-2 text-xs font-bold text-white line-clamp-1">{area.name}</h4>
                      <p className="text-[11px] text-slate-400 font-mono mt-0.5">Geohash: {area.geohash5}</p>
                      <span className="mt-2 inline-block rounded-full bg-emerald-950 px-2 py-0.5 text-[10px] font-semibold text-emerald-400 border border-emerald-800/50">
                        {area.count} active items
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
