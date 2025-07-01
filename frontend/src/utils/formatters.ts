// frontend/src/utils/formatters.ts

/**
 * Utility functions for formatting numbers, currency, and other data types
 * following Colombian standards and practices
 */

/**
 * Format a number as Colombian pesos (COP)
 * @param value - The number to format
 * @param options - Additional formatting options
 * @returns Formatted currency string
 */
export const formatCurrency = (
  value: number, 
  options: {
    minimumFractionDigits?: number;
    maximumFractionDigits?: number;
    showSymbol?: boolean;
  } = {}
): string => {
  const {
    minimumFractionDigits = 0,
    maximumFractionDigits = 0,
    showSymbol = true
  } = options;

  if (showSymbol) {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits,
      maximumFractionDigits,
    }).format(value);
  } else {
    return new Intl.NumberFormat('es-CO', {
      minimumFractionDigits,
      maximumFractionDigits,
    }).format(value);
  }
};

/**
 * Format a number with Colombian locale (thousands separators)
 * @param value - The number to format
 * @returns Formatted number string
 */
export const formatNumber = (value: number): string => {
  return new Intl.NumberFormat('es-CO').format(value);
};

/**
 * Format a number as percentage
 * @param value - The number to format (as decimal, e.g., 0.15 for 15%)
 * @param options - Additional formatting options
 * @returns Formatted percentage string
 */
export const formatPercentage = (
  value: number,
  options: {
    minimumFractionDigits?: number;
    maximumFractionDigits?: number;
  } = {}
): string => {
  const {
    minimumFractionDigits = 1,
    maximumFractionDigits = 2
  } = options;

  return new Intl.NumberFormat('es-CO', {
    style: 'percent',
    minimumFractionDigits,
    maximumFractionDigits,
  }).format(value);
};

/**
 * Format a date according to Colombian locale
 * @param date - The date to format
 * @param options - Formatting options
 * @returns Formatted date string
 */
export const formatDate = (
  date: Date | string,
  options: {
    dateStyle?: 'full' | 'long' | 'medium' | 'short';
    timeStyle?: 'full' | 'long' | 'medium' | 'short';
    includeTime?: boolean;
  } = {}
): string => {
  const {
    dateStyle = 'medium',
    timeStyle = 'short',
    includeTime = false
  } = options;

  const dateObj = typeof date === 'string' ? new Date(date) : date;

  if (includeTime) {
    return new Intl.DateTimeFormat('es-CO', {
      dateStyle,
      timeStyle
    }).format(dateObj);
  } else {
    return new Intl.DateTimeFormat('es-CO', {
      dateStyle
    }).format(dateObj);
  }
};

/**
 * Format a relative date (e.g., "hace 2 días", "en 3 horas")
 * @param date - The date to format
 * @returns Formatted relative date string
 */
export const formatRelativeDate = (date: Date | string): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);

  const rtf = new Intl.RelativeTimeFormat('es-CO', { numeric: 'auto' });

  if (Math.abs(diffInSeconds) < 60) {
    return 'hace un momento';
  } else if (Math.abs(diffInSeconds) < 3600) {
    const minutes = Math.floor(diffInSeconds / 60);
    return rtf.format(-minutes, 'minute');
  } else if (Math.abs(diffInSeconds) < 86400) {
    const hours = Math.floor(diffInSeconds / 3600);
    return rtf.format(-hours, 'hour');
  } else if (Math.abs(diffInSeconds) < 2592000) {
    const days = Math.floor(diffInSeconds / 86400);
    return rtf.format(-days, 'day');
  } else if (Math.abs(diffInSeconds) < 31536000) {
    const months = Math.floor(diffInSeconds / 2592000);
    return rtf.format(-months, 'month');
  } else {
    const years = Math.floor(diffInSeconds / 31536000);
    return rtf.format(-years, 'year');
  }
};

/**
 * Format file size in human-readable format
 * @param bytes - File size in bytes
 * @returns Formatted file size string
 */
export const formatFileSize = (bytes: number): string => {
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  
  if (bytes === 0) return '0 Bytes';
  
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  const size = bytes / Math.pow(1024, i);
  
  return `${size.toFixed(i === 0 ? 0 : 1)} ${sizes[i]}`;
};

/**
 * Format a Colombian tax identification number (NIT)
 * @param nit - The NIT to format
 * @param includeCheckDigit - Whether to include the check digit
 * @returns Formatted NIT string
 */
export const formatNIT = (
  nit: string | number, 
  includeCheckDigit: boolean = true
): string => {
  const nitStr = String(nit).replace(/\D/g, '');
  
  if (nitStr.length < 3) return nitStr;
  
  // Split NIT and check digit
  const mainNit = nitStr.slice(0, -1);
  const checkDigit = nitStr.slice(-1);
  
  // Format with thousands separators
  const formattedNit = mainNit.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  
  return includeCheckDigit ? `${formattedNit}-${checkDigit}` : formattedNit;
};

/**
 * Truncate text with ellipsis
 * @param text - Text to truncate
 * @param maxLength - Maximum length before truncation
 * @returns Truncated text
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength).trim() + '...';
};

/**
 * Calculate and format tax rate percentage
 * @param grossAmount - Gross amount
 * @param taxAmount - Tax/retention amount
 * @returns Formatted tax rate percentage
 */
export const calculateTaxRate = (
  grossAmount: number, 
  taxAmount: number
): string => {
  if (grossAmount === 0) return '0%';
  
  const rate = (taxAmount / grossAmount);
  return formatPercentage(rate, { maximumFractionDigits: 2 });
};

/**
 * Format currency for display in tables (shorter format)
 * @param value - The number to format
 * @returns Formatted currency string for tables
 */
export const formatCurrencyCompact = (value: number): string => {
  if (Math.abs(value) >= 1000000000) {
    return `$${(value / 1000000000).toFixed(1)}B`;
  } else if (Math.abs(value) >= 1000000) {
    return `$${(value / 1000000).toFixed(1)}M`;
  } else if (Math.abs(value) >= 1000) {
    return `$${(value / 1000).toFixed(0)}K`;
  } else {
    return formatCurrency(value);
  }
};

// Export commonly used format combinations
export const commonFormats = {
  currencyWithoutSymbol: (value: number) => formatCurrency(value, { showSymbol: false }),
  shortDate: (date: Date | string) => formatDate(date, { dateStyle: 'short' }),
  longDate: (date: Date | string) => formatDate(date, { dateStyle: 'long' }),
  dateWithTime: (date: Date | string) => formatDate(date, { 
    dateStyle: 'medium', 
    includeTime: true 
  }),
  compactNumber: (value: number) => {
    if (Math.abs(value) >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`;
    } else if (Math.abs(value) >= 1000) {
      return `${(value / 1000).toFixed(0)}K`;
    } else {
      return formatNumber(value);
    }
  }
};

// Type definitions for better TypeScript support
export type CurrencyFormatOptions = Parameters<typeof formatCurrency>[1];
export type DateFormatOptions = Parameters<typeof formatDate>[1];
export type PercentageFormatOptions = Parameters<typeof formatPercentage>[1];
