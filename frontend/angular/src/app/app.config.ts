export enum PageType {
  UNDEFINED = 'UNDEFINED',
  LOGIN = 'LOGIN',
  INTAKE = 'INTAKE',
  FETCH = 'FETCH',
  STUDIES = 'STUDIES',
  VIEW_REPORT = 'VIEW_REPORT',
}

export const WhiteLabel = [
  {
    url: /ucla[0-9]*\.spineai/g,
    logoImg: 'assets/img/ucla_logo.png',
    logoCss: [],
    showSubLogo: true
  },
  {
    url: /geisinger[0-9]*.spineai/g,
    logoImg: 'assets/img/geisinger_logo.png',
    logoCss: [
      ['margin-top', '20px'],
      ['margin-bottom', '-10px']
    ],
    showSubLogo: true
  },
  {
    url: /hopkins[0-9]*.spineai/g,
    logoImg: 'assets/img/hopkins_logo.jpg',
    logoCss: [
    ],
    showSubLogo: true
  },
  {
    url: /bilh[0-9]*.spineai/g,
    logoImg: 'assets/img/bilh_logo.png',
    logoCss: [
    ],
    showSubLogo: true
  }
]


