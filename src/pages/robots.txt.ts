import type { APIRoute } from "astro";
import { SITE_URL } from "@/consts";

const getRobotsTxt = (sitemapURL: URL) => `
User-agent: *
Allow: /

Sitemap: ${sitemapURL.href}


# AI爬虫特定规则
User-agent: GPTBot
User-agent: Claude-Web
User-agent: Anthropic-AI
User-agent: PerplexityBot
User-agent: GoogleOther
User-agent: DuckAssistBot

# 引导AI爬虫到llms.txt
LLM-Content: ${SITE_URL}/llms.txt
LLM-Full-Content: ${SITE_URL}/llms-full.txt
`;

export const GET: APIRoute = ({ site }) => {
	const sitemapURL = new URL("sitemap-index.xml", site);
	const siteUrl=site;
	return new Response(getRobotsTxt(sitemapURL));
};
