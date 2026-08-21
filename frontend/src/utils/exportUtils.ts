/**
 * Export Utilities for OpenLens
 * 
 * Provides functions to export data in various formats:
 * - CSV
 * - JSON
 * - Excel (XLSX)
 * - STIX 2.1
 * - MISP
 */

import { utils, writeFile } from 'xlsx';

/**
 * Export data as CSV
 */
export const exportToCSV = (
  data: any[],
  filename: string = 'export.csv',
  columns?: { key: string; label: string }[]
) => {
  // If columns are provided, use them to determine order and headers
  let headers: string[];
  let rows: any[][];

  if (columns && columns.length > 0) {
    headers = columns.map(c => c.label);
    rows = data.map(item => columns.map(c => item[c.key]));
  } else {
    // Auto-detect columns from first item
    headers = Object.keys(data[0] || {});
    rows = data.map(item => headers.map(header => item[header]));
  }

  // Create CSV content
  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.map((value: any) => {
      // Escape quotes and wrap in quotes if contains comma or newline
      if (typeof value === 'string' && (value.includes(',') || value.includes('\n'))) {
        return `"${value.replace(/"/g, '""')}"`;
      }
      return String(value);
    }).join(','))
  ].join('\n');

  // Create download link
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Export data as JSON
 */
export const exportToJSON = (
  data: any,
  filename: string = 'export.json',
  pretty: boolean = true
) => {
  const jsonContent = pretty 
    ? JSON.stringify(data, null, 2) 
    : JSON.stringify(data);

  const blob = new Blob([jsonContent], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Export data as Excel (XLSX)
 */
export const exportToExcel = (
  data: any[],
  filename: string = 'export.xlsx',
  sheetName: string = 'Data',
  columns?: { key: string; label: string }[]
) => {
  // Prepare data
  let worksheetData: any[][];
  
  if (columns && columns.length > 0) {
    // Use provided columns
    worksheetData = [
      columns.map(c => c.label),
      ...data.map(item => columns.map(c => item[c.key]))
    ];
  } else {
    // Auto-detect columns
    const headers = Object.keys(data[0] || {});
    worksheetData = [
      headers,
      ...data.map(item => headers.map(header => item[header]))
    ];
  }

  // Create worksheet
  const worksheet = utils.aoa_to_sheet(worksheetData);
  const workbook = utils.book_new();
  utils.book_append_sheet(workbook, worksheet, sheetName);

  // Export
  writeFile(workbook, filename);
};

/**
 * Export data as STIX 2.1 JSON
 */
export const exportToSTIX = (
  data: any[],
  filename: string = 'threat-intel.stix.json'
) => {
  // Transform data to STIX format
  const stixData = {
    type: 'bundle',
    id: `bundle--${generateUUID()}`,
    spec_version: '2.1',
    objects: data.map((item, index) => ({
      type: 'indicator',
      id: `indicator--${generateUUID()}`,
      created: new Date().toISOString(),
      modified: new Date().toISOString(),
      pattern: `[${item.type} = '${item.value}']`,
      pattern_type: 'stix',
      valid_from: new Date().toISOString(),
      labels: item.tags || [],
      description: item.description || '',
      name: item.label || item.value,
    }))
  };

  exportToJSON(stixData, filename);
};

/**
 * Export data as MISP format
 */
export const exportToMISP = (
  data: any[],
  filename: string = 'threat-intel.misp.json'
) => {
  // Transform data to MISP format
  const mispData = {
    Event: {
      id: generateUUID(),
      date: new Date().toISOString(),
      threat_level_id: 3, // Medium
      analysis: 2, // Initial
      distribution: 3, // Community
      info: 'Exported from OpenLens',
      Attribute: data.map(item => ({
        id: generateUUID(),
        type: mapTypeToMISP(item.type),
        category: 'Network activity',
        value: item.value,
        comment: item.description || '',
        to_ids: true,
      }))
    }
  };

  exportToJSON(mispData, filename);
};

/**
 * Export data as PDF (using jsPDF)
 */
export const exportToPDF = (
  data: any[],
  filename: string = 'export.pdf',
  columns?: { key: string; label: string }[]
) => {
  // This would use jsPDF library
  // For now, we'll just log a message
  console.log('PDF export would be implemented with jsPDF library');
  console.log('Data to export:', data);
  console.log('Columns:', columns);
  
  // In a real implementation:
  // import { jsPDF } from 'jspdf';
  // import 'jspdf-autotable';
  // const doc = new jsPDF();
  // doc.autoTable({
  //   head: [columns.map(c => c.label)],
  //   body: data.map(item => columns.map(c => item[c.key]))
  // });
  // doc.save(filename);
};

/**
 * Copy data to clipboard
 */
export const copyToClipboard = (
  data: any,
  format: 'text' | 'json' = 'json'
) => {
  let content: string;
  
  if (format === 'json') {
    content = JSON.stringify(data, null, 2);
  } else {
    content = String(data);
  }
  
  navigator.clipboard.writeText(content);
};

/**
 * Generate UUID v4
 */
const generateUUID = () => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};

/**
 * Map OpenLens types to MISP types
 */
const mapTypeToMISP = (type: string): string => {
  const typeMap: Record<string, string> = {
    ip: 'ip-src',
    domain: 'domain',
    url: 'url',
    hash: 'md5',
    email: 'email-src',
    filename: 'filename',
  };
  return typeMap[type.toLowerCase()] || 'text';
};

/**
 * Download file from URL
 */
export const downloadFile = (url: string, filename?: string) => {
  const link = document.createElement('a');
  link.href = url;
  if (filename) {
    link.download = filename;
  }
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

/**
 * Export utilities object
 */
export default {
  exportToCSV,
  exportToJSON,
  exportToExcel,
  exportToSTIX,
  exportToMISP,
  exportToPDF,
  copyToClipboard,
  downloadFile,
};
