// locales settings for this theme
// Set the languages you want to support on your site.
// https://astro-i18n-starter.pages.dev/setup/

export const DEFAULT_LOCALE_SETTING: string = "en";

interface LocaleSetting {
	[key: Lowercase<string>]: {
		label: string;
		lang?: string;
		dir?: "rtl" | "ltr";
	};
} // refer: https://starlight.astro.build/reference/configuration/#locales

export const LOCALES_SETTING: LocaleSetting = {
	en: {
		label: "English",
		lang: "en-US",
	},
	es: {
		label: "Español",
		lang: "es-ES",
	},
	fr: {
		label: "Français",
		lang: "fr-FR",
	},
	de: {
		label: "Deutsch",
		lang: "de-DE",
	},
	ja: {
		label: "日本語",
		lang: "ja-JP",
	},
	"zh-cn": {
		label: "简体中文",
		lang: "zh-CN",
	},
	ru: {
		label: "Русский",
		lang: "ru-RU",
	},
	pt: {
		label: "Português",
		lang: "pt-BR",
	},
	ar: {
		label: "العربية",
		lang: "ar-SA",
		dir: "rtl",
	},
	ko: {
		label: "한국어",
		lang: "ko-KR",
	},
};
