/** electron-vite kopiert `?asset`-Importe ins Bundle und liefert den Pfad. */
declare module '*?asset' {
  const src: string
  export default src
}
