import type { SidebarsConfig } from '@docusaurus/plugin-content-docs'

const sidebars: SidebarsConfig = {
  docsSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      collapsed: false,
      items: ['getting-started/installation', 'getting-started/quick-start'],
    },
    {
      type: 'category',
      label: 'Architecture',
      items: ['architecture/overview', 'architecture/monorepo', 'architecture/database'],
    },
    {
      type: 'category',
      label: 'Multi-Agent System',
      items: ['agents/overview', 'agents/graphs', 'agents/modes'],
    },
    {
      type: 'category',
      label: 'Frontend',
      items: ['frontend/overview'],
    },
    {
      type: 'category',
      label: 'Backend',
      items: ['backend/overview', 'backend/api-reference'],
    },
  ],
}

export default sidebars
