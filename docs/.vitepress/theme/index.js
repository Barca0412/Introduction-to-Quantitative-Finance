import DefaultTheme from 'vitepress/theme'
import PapersList from './components/PapersList.vue'
import PaperCard from './components/PaperCard.vue'
import TrendsChart from './components/TrendsChart.vue'
import IconWrapper from './components/IconWrapper.vue'
import './style.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('PapersList', PapersList)
    app.component('PaperCard', PaperCard)
    app.component('TrendsChart', TrendsChart)
    app.component('IconWrapper', IconWrapper)
  }
}
