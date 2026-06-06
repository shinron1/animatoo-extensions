// ==MiruExtension==
// @name         Azora Manga
// @version      v1.0.0
// @author       you
// @lang         ar
// @license      MIT
// @icon         https://azoramoon.com/favicon.ico
// @package      com.arab.azoramanga
// @type         manga
// @webSite      https://azoramoon.com
// @description  مانجا، مانهوا، ومانها من Azora Manga
// ==/MiruExtension==

const API = "https://api.azoramoon.com"

export default class extends Extension {
  async req(path) {
    return this.request(path, {
      headers: { "Miru-Url": API, "Referer": "https://azoramoon.com" }
    })
  }

  async latest(page) {
    const body = await this.req("/api/posts?page=" + page + "&perPage=20")
    const data = JSON.parse(body)
    return data.posts.map(p => ({
      title: p.postTitle,
      url: "/detail/" + p.slug + "?id=" + p.id,
      cover: p.featuredImage,
      headers: { "Referer": "https://azoramoon.com" }
    }))
  }

  async search(kw, page, filter) {
    let path = "/api/posts?page=" + page + "&perPage=20"
    if (kw) path += "&q=" + encodeURIComponent(kw)
    const body = await this.req(path)
    const data = JSON.parse(body)
    let list = data.posts || []
    if (filter && filter.genre && filter.genre[0] !== "all" && data.posts) {
      const gid = parseInt(filter.genre[0])
      list = list.filter(p => p.genres && p.genres.some(g => g.id === gid))
    }
    return list.map(p => ({
      title: p.postTitle,
      url: "/detail/" + p.slug + "?id=" + p.id,
      cover: p.featuredImage,
      headers: { "Referer": "https://azoramoon.com" }
    }))
  }

  async createFilter() {
    const body = await this.req("/api/genres")
    const genres = JSON.parse(body)
    const opts = { all: "الكل" }
    for (const g of genres) opts[g.id] = g.name
    return { genre: { title: "التصنيف", min: 1, max: 1, default: "all", options: opts } }
  }

  async detail(url) {
    const qIdx = url.indexOf("?")
    const slug = url.substring(url.indexOf("/detail/") + 8, qIdx > -1 ? qIdx : undefined)
    const params = qIdx > -1 ? new URLSearchParams(url.substring(qIdx)) : new URLSearchParams()
    let postId = params.get("id") ? parseInt(params.get("id")) : null

    if (!postId) {
      try {
        const html = await this.request("/series/" + slug)
        const pidRaw = /postId(?:&quot;|"):\s*\[0,(\d+)\]/.exec(html)
        if (pidRaw) postId = parseInt(pidRaw[1])
        if (!postId) {
          const mpidRaw = /mangaPostId(?:&quot;|"|":)(\d+)/.exec(html)
          if (mpidRaw) postId = parseInt(mpidRaw[1])
        }
      } catch (e) {}
    }

    if (postId) {
      try {
        const chBody = await this.req("/api/chapters?postId=" + postId + "&perPage=200")
        const chData = JSON.parse(chBody)
        const p = chData.post
        const accessible = (p?.chapters || []).filter(c => c.isAccessible)
        accessible.sort((a, b) => b.number - a.number)
        return {
          title: p?.postTitle || slug,
          cover: p?.featuredImage || "",
          desc: "",
          headers: { "Referer": "https://azoramoon.com" },
          episodes: [{
            title: "الفصول",
            urls: accessible.map(c => ({
              name: c.title ? "الفصل " + c.number + " - " + c.title : "الفصل " + c.number,
              url: "/chapter/" + slug + "/" + c.slug
            }))
          }]
        }
      } catch (e) {}
    }
    return { title: slug, cover: "", desc: "", headers: { "Referer": "https://azoramoon.com" }, episodes: [] }
  }

  async watch(url) {
    const parts = url.split("/chapter/")[1]
    const [slug, chapterSlug] = parts.split("/")
    const html = await this.request("/series/" + slug + "/" + chapterSlug)
    const urls = []
    const regex = /<img[^>]+data-reader-page-image[^>]+src="([^"]+)"[^>]*>/g
    let m
    while ((m = regex.exec(html)) !== null) {
      urls.push(m[1])
    }
    return { urls }
  }

  async checkUpdate(url) {
    return ""
  }
}
