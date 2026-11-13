import { defineAsyncComponent, h } from 'vue'
import DefaultTheme from 'vitepress/theme'
import { useRoute } from 'vitepress'
import './style.css'

// Radar components (and echarts / the data loader they pull in) are split into
// their own chunks, so non-Radar pages never download them.
const PapersList = defineAsyncComponent(() => import('./components/PapersList.vue'))
const PaperCard = defineAsyncComponent(() => import('./components/PaperCard.vue'))
const TrendsChart = defineAsyncComponent(() => import('./components/TrendsChart.vue'))
// IconWrapper imports every lucide icon, so it must not sit in the main chunk either.
const IconWrapper = defineAsyncComponent(() => import('./components/IconWrapper.vue'))

// arXiv asks API users to show this acknowledgement wherever its data is used.
const ARXIV_ACKNOWLEDGEMENT = 'Thank you to arXiv for use of its open access interoperability.'

const RadarAttribution = {
  setup() {
    const route = useRoute()
    return () => (/\/arxiv(\/|$)/.test(route.path)
      ? h('p', { class: 'arxiv-attribution' }, [
          ARXIV_ACKNOWLEDGEMENT,
          ' This site shows arXiv metadata and abstracts only; full texts and figures stay on ',
          h('a', { href: 'https://arxiv.org', target: '_blank', rel: 'noopener' }, 'arxiv.org'),
          '.',
        ])
      : null)
  },
}

export default {
  extends: DefaultTheme,
  Layout() {
    return h(DefaultTheme.Layout, null, {
      'layout-bottom': () => h(RadarAttribution),
    })
  },
  enhanceApp({ app }) {
    app.component('PapersList', PapersList)
    app.component('PaperCard', PaperCard)
    app.component('TrendsChart', TrendsChart)
    app.component('IconWrapper', IconWrapper)
  }
}
