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
const GENRES = { all: "الكل" }

export default class extends Extension {
  async req(path, opts) {
    return this.request(path, {
      headers: { "Miru-Url": API, "Referer": "https://azoramoon.com", ...opts?.headers }
    })
  }

  async latest(page) {
    const body = await this.req("/api/posts?page=" + page + "&perPage=20")
    const data = JSON.parse(body)
    return data.posts.map(p => ({
      title: p.postTitle,
      url: "/detail/" + p.slug,
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
      url: "/detail/" + p.slug,
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
    const slug = url.split("/detail/")[1]
    const html = await this.request("/series/" + slug)
    const descMatch = /<meta\s+name="description"\s+content="([^"]+)"/.exec(html)
    const desc = descMatch ? descMatch[1] : ""
    let postId = null
    const pidRaw = /postId(?:&quot;|"):\s*\[0,(\d+)\]/.exec(html)
    if (pidRaw) postId = parseInt(pidRaw[1])
    if (!postId) {
      const mpidRaw = /mangaPostId(?:&quot;|"|":)(\d+)/.exec(html)
      if (mpidRaw) postId = parseInt(mpidRaw[1])
    }
    const titleMatch = /<meta\s+property="og:title"\s+content="([^"]+)"/.exec(html)
    const title = titleMatch ? titleMatch[1] : slug
    const coverMatch = /<meta\s+property="og:image"\s+content="([^"]+)"/.exec(html)
    const cover = coverMatch ? coverMatch[1] : ""

    if (postId) {
      try {
        const chBody = await this.req("/api/chapters?postId=" + postId + "&perPage=999")
        const chData = JSON.parse(chBody)
        const accessible = (chData.post?.chapters || []).filter(c => c.isAccessible)
        accessible.sort((a, b) => b.number - a.number)
        return {
          title, cover, desc,
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
    return { title, cover, desc, headers: { "Referer": "https://azoramoon.com" }, episodes: [] }
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
