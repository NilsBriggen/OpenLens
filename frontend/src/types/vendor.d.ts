// Ambient declarations for vendor packages that ship no types.
// This file must stay import-free: a top-level import would turn it into a
// module, making `declare module` an (invalid) augmentation of a package
// that has no types. The leaflet augmentation lives in leaflet-heat.d.ts.

declare module 'react-cytoscapejs';
