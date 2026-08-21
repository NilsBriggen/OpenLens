/// <reference types="vite/client" />

/**
 * The app predates the move to Vite and still reads its configuration through
 * `REACT_APP_*` variables, which vite.config.ts exposes via `envPrefix`.
 */
interface ImportMetaEnv {
  readonly REACT_APP_API_URL?: string;
  readonly REACT_APP_WS_URL?: string;
  readonly REACT_APP_ENV?: string;
  readonly REACT_APP_VERSION?: string;
  readonly REACT_APP_NAME?: string;
  readonly REACT_APP_ENABLE_ANALYTICS?: string;
  readonly REACT_APP_ENABLE_AI?: string;
  readonly REACT_APP_ENABLE_WEBSOCKET?: string;
  readonly REACT_APP_ENABLE_SCRAPING?: string;
  readonly REACT_APP_ENABLE_THREAT_INTEL?: string;
  readonly REACT_APP_DEBUG?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
