export default {
  async fetch(request) {
    if (request.method !== "GET") {
      return new Response("Method not allowed", { status: 405 });
    }

    const substackUrl = "https://johndamask.substack.com/feed";

    try {
      const response = await fetch(substackUrl, {
        headers: {
          "User-Agent": "Mozilla/5.0 (compatible; SubstackRSSProxy/1.0)",
        },
      });

      if (!response.ok) {
        return new Response(`Upstream error: ${response.status}`, {
          status: 502,
        });
      }

      const body = await response.text();

      return new Response(body, {
        status: 200,
        headers: {
          "Content-Type": "application/xml; charset=utf-8",
          "Cache-Control": "public, max-age=900",
        },
      });
    } catch (err) {
      return new Response(`Fetch failed: ${err.message}`, { status: 502 });
    }
  },
};
