// Place any global data in this file.
// You can import this data from anywhere in your site by using the `import` keyword.

import type { Multilingual } from "@/i18n";

export const SITE_TITLE: string | Multilingual = "happy ghast";

export const SITE_DESCRIPTION: string | Multilingual = {
	en: "A news and information integration site about happy ghast in Minecraft.",
	es: "Un sitio de integración de noticias e información sobre happy ghast en Minecraft.",
	fr: "Un site d'intégration de nouvelles et d'informations sur happy ghast dans Minecraft.",
	de: "Eine Nachrichten- und Informationsintegrationsseite über happy ghast in Minecraft.",
	ja: "Minecraft の happy ghast に関するニュースと情報を統合したサイト。",
	"zh-cn": "我的世界中关于 happy ghast 的新闻与信息整合站点。",
	ru: "Сайт интеграции новостей и информации о happy ghast в Minecraft.",
	pt: "Um site de integração de notícias e informações sobre happy ghast no Minecraft.",
	ar: "موقع تكامل الأخبار والمعلومات حول happy ghast في Minecraft.",
	ko: "Minecraft의 happy ghast에 관한 뉴스 및 정보 통합 사이트.",
};

export const X_ACCOUNT: string | Multilingual = "@psephopaiktes";

export const NOT_TRANSLATED_CAUTION: string | Multilingual = {
	en: "This page is not available in your language.",
	es: "Esta página no está disponible en tu idioma.",
	fr: "Cette page n'est pas disponible dans votre langue.",
	de: "Diese Seite ist in Ihrer Sprache nicht verfügbar.",
	ja: "このページはご利用の言語でご覧いただけません。",
	"zh-cn": "此页面不支持您的语言。",
	ru: "Эта страница недоступна на вашем языке.",
	pt: "Esta página não está disponível no seu idioma.",
	ar: "هذه الصفحة غير متوفرة بلغتك.",
	ko: "이 페이지는 귀하의 언어로 제공되지 않습니다.",
};
