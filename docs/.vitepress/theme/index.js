import { defineAsyncComponent, h } from 'vue'
import DefaultTheme from 'vitepress/theme'
import { useRoute } from 'vitepress'
import './style.css'
// Lecture/knowledge-base glue: small, and needed on lecture and wiki pages.
import TutorialMeta from './components/TutorialMeta.vue'
import TutorialList from './components/TutorialList.vue'
import WikiBacklinks from './components/WikiBacklinks.vue'

// Radar components (and echarts / the data loader they pull in) are split into
// their own chunks, so non-Radar pages never download them.
const PapersList = defineAsyncComponent(() => import('./components/PapersList.vue'))
const PaperCard = defineAsyncComponent(() => import('./components/PaperCard.vue'))
const TrendsChart = defineAsyncComponent(() => import('./components/TrendsChart.vue'))
// IconWrapper imports every lucide icon, so it must not sit in the main chunk either.
const IconWrapper = defineAsyncComponent(() => import('./components/IconWrapper.vue'))

// arXiv asks API users to show this acknowledgement wherever its data is used.
const ARXIV_ACKNOWLEDGEMENT = 'Thank you to arXiv for use of its open access interoperability.'

// Injected by docs/.vitepress/config.ts from HF_DATASET_REPO at build time.
const HF_DATASET_REPO = __HF_DATASET_REPO__
const RADAR_RELEASE_URL = __RADAR_RELEASE_URL__

const externalLink = (href, text) => h('a', { href, target: '_blank', rel: 'noopener' }, text)

// "Full dataset: Hugging Face · GitHub Release mirror"; the HF link only when configured.
export const RadarDatasetLinks = {
  setup() {
    return () => {
      const links = []
      if (HF_DATASET_REPO) {
        links.push(externalLink(`https://huggingface.co/datasets/${HF_DATASET_REPO}`, 'Hugging Face'), ' · ')
      }
      links.push(externalLink(RADAR_RELEASE_URL, 'GitHub Release mirror'))
      return h('span', { class: 'radar-dataset-links' }, ['Full dataset (CC BY 4.0): ', ...links])
    }
  },
}

const RadarAttribution = {
  setup() {
    const route = useRoute()
    return () => (/\/arxiv(\/|$)/.test(route.path)
      ? h('p', { class: 'arxiv-attribution' }, [
          'FinPaperRadar · AI × 金融论文雷达. ',
          ARXIV_ACKNOWLEDGEMENT,
          ' This site shows arXiv metadata and abstracts only; full texts and figures stay on ',
          externalLink('https://arxiv.org', 'arxiv.org'),
          '. ',
          h(RadarDatasetLinks),
        ])
      : null)
  },
}

export default {
  extends: DefaultTheme,
  Layout() {
    return h(DefaultTheme.Layout, null, {
      'doc-before': () => h(TutorialMeta),
      'doc-after': () => h(WikiBacklinks),
      'layout-bottom': () => h(RadarAttribution),
    })
  },
  enhanceApp({ app }) {
    app.component('PapersList', PapersList)
    app.component('PaperCard', PaperCard)
    app.component('TrendsChart', TrendsChart)
    app.component('IconWrapper', IconWrapper)
    app.component('RadarDatasetLinks', RadarDatasetLinks)
    app.component('TutorialList', TutorialList)
  }
}
