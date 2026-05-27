import { themes as prismThemes } from "prism-react-renderer";
import type { Config } from "@docusaurus/types";
import type * as Preset from "@docusaurus/preset-classic";

const config: Config = {
  title: "Conflow Docs",
  tagline: "AI-powered IT Collaboration Platform for University Study Teams",
  favicon: "img/favicon.ico",

  url: "https://conflow-docs.example.com",
  baseUrl: "/",

  organizationName: "conflow",
  projectName: "conflow",

  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",

  i18n: {
    defaultLocale: "ko",
    locales: ["ko"],
  },

  markdown: {
    mermaid: true,
  },
  themes: ["@docusaurus/theme-mermaid"],

  presets: [
    [
      "classic",
      {
        docs: {
          sidebarPath: "./sidebars.ts",
          routeBasePath: "docs",
          editUrl: "https://github.com/conflow/conflow/tree/main/docs-site/",
        },
        blog: false,
        theme: {
          customCss: "./src/css/custom.css",
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: "img/conflow-social-card.png",
    navbar: {
      title: "Conflow",
      logo: {
        alt: "Conflow Logo",
        src: "img/logo.svg",
      },
      items: [
        {
          type: "docSidebar",
          sidebarId: "docsSidebar",
          position: "left",
          label: "Documentation",
        },
        {
          href: "https://github.com/conflow/conflow",
          label: "GitHub",
          position: "right",
        },
      ],
    },
    footer: {
      style: "dark",
      links: [
        {
          title: "Docs",
          items: [
            { label: "Introduction", to: "/docs/intro" },
            { label: "Getting Started", to: "/docs/getting-started/installation" },
            { label: "Architecture", to: "/docs/architecture/overview" },
          ],
        },
        {
          title: "Agents",
          items: [
            { label: "Overview", to: "/docs/agents/overview" },
            { label: "Graphs", to: "/docs/agents/graphs" },
            { label: "Modes", to: "/docs/agents/modes" },
          ],
        },
        {
          title: "More",
          items: [
            {
              label: "GitHub",
              href: "https://github.com/conflow/conflow",
            },
          ],
        },
      ],
      copyright: `Copyright ${new Date().getFullYear()} Conflow. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ["bash", "python", "json", "toml"],
    },
    mermaid: {
      theme: { light: "neutral", dark: "dark" },
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
