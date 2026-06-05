// ==MiruExtension==
// @name       anime3rb
// @version    v1.0.0
// @author     you
// @lang       ar
// @license    MIT
// @icon       https://anime3rb.com/favicon.ico
// @package    com.arab.anime3rb
// @type       bangumi
// @webSite    https://anime3rb.com
// @description أنمي من Supabase
// ==/MiruExtension==

const SUPABASE_URL = "https://iwccaogufwaqzrodojvh.supabase.co/rest/v1"
const ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml3Y2Nhb2d1ZndhcXpyb2RvanZoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkxMTMxNjUsImV4cCI6MjA5NDY4OTE2NX0.hEl_v7cfd1lZMqI3QJAk2eaX-AFw3C_TAAWpkSMMGwk"

const SB_HEADERS = {
  "Miru-Url": SUPABASE_URL + "/",
  "apikey": ANON_KEY,
  "Authorization": "Bearer " + ANON_KEY,
  "Prefer": "count=exact"
}

export default class extends Extension {
  async latest(page) {
    const res = await this.request("/anime?select=id,slug,title,title_ar,type,episode_count,poster_url,rating,status&poster_url=not.is.null&order=created_at.desc&limit=20&offset=" + ((page - 1) * 20), { headers: SB_HEADERS })
    return res.map(item => ({
      title: item.title_ar || item.title,
      url: "/detail/" + item.id,
      cover: item.poster_url,
      update: item.status,
      headers: { "Referer": "https://anilist.co" }
    }))
  }

  async search(kw, page, filter) {
    let base = "/anime?select=id,slug,title,title_ar,type,episode_count,poster_url,rating,status&poster_url=not.is.null&limit=20&offset=" + ((page - 1) * 20)
    if (kw) {
      base += "&or=(title_ar.ilike.*" + kw + "*,title.ilike.*" + kw + "*)"
    }
    if (filter && filter.genre && filter.genre[0] !== "all") {
      base += "&anime_genres=not.is.null&anime_genres.genre_id=eq." + filter.genre[0]
    }
    const res = await this.request(base, { headers: SB_HEADERS })
    return res.map(item => ({
      title: item.title_ar || item.title,
      url: "/detail/" + item.id,
      cover: item.poster_url,
      update: item.type,
      headers: { "Referer": "https://anilist.co" }
    }))
  }

  async createFilter(filter) {
    const res = await this.request("/genres?select=id,slug,name_ar&order=name_ar", { headers: SB_HEADERS })
    const options = { all: "الكل" }
    res.forEach(g => { options[g.id] = g.name_ar })
    return {
      genre: {
        title: "التصنيف",
        min: 1,
        max: 1,
        default: "all",
        options: options
      }
    }
  }

  async detail(url) {
    const id = url.split("/detail/")[1]
    const animeRes = await this.request("/anime?id=eq." + id + "&select=*", { headers: SB_HEADERS })
    if (!animeRes || animeRes.length === 0) throw new Error("Anime not found")
    const a = animeRes[0]

    const epRes = await this.request("/episodes?anime_id=eq." + id + "&select=id,number,title,url,duration&order=number", { headers: SB_HEADERS })

    return {
      title: a.title_ar || a.title,
      cover: a.poster_url,
      desc: a.synopsis,
      headers: { "Referer": "https://anilist.co" },
      episodes: [{
        title: "الحلقات",
        urls: (epRes || []).map(ep => ({
          name: ep.number + " - " + (ep.title || "حلقة " + ep.number),
          url: ep.url
        }))
      }]
    }
  }

  async watch(url) {
    const path = url.includes("/") && !url.startsWith("http")
      ? url
      : "/" + url.split("anime3rb.com").pop().replace(/^\//, "")

    const html = await this.request(path)
    const m = /video_url&quot;:&quot;(https?:\\\/\\\/video[^&]+token=[a-f0-9]+)&amp;expires=(\d+)&quot;/.exec(html)
    if (!m) throw new Error("video_url not found")
    const playerUrl = m[1].replace(/\\\//g, "/") + "&expires=" + m[2]

    const parts = playerUrl.split("://")[1]
    const host = parts.split("/")[0]
    const ppath = "/" + parts.split("/").slice(1).join("/")

    const playerHtml = await this.request(ppath, {
      headers: { "Miru-Url": "https://" + host, "Referer": "https://anime3rb.com" }
    })
    const vsMatches = playerHtml.match(/video_sources\s*=\s*(\[[^;]+?\])\s*;/g)
    if (!vsMatches) throw new Error("video_sources not found")
    const last = vsMatches[vsMatches.length - 1]
    const vs = /video_sources\s*=\s*(\[[^;]+?\])\s*;/.exec(last)
    const sources = JSON.parse(vs[1])

    const labels = ["4k", "1080p", "720p", "480p", "360p", "auto"]
    const filtered = sources.filter(s =>
      labels.includes((s.label || "").toLowerCase().trim())
    )
    filtered.sort((a, b) => {
      const q = { "4k": 4, "1080p": 3, "720p": 2, "480p": 1, "360p": 0, "auto": 0 }
      return (q[b.label] || 0) - (q[a.label] || 0)
    })
    const best = filtered[0]
    return {
      type: best.src.includes(".m3u8") ? "hls" : "mp4",
      url: best.src,
      headers: { "Referer": "https://anime3rb.com" }
    }
  }

  async checkUpdate(url) {
    return ""
  }
}