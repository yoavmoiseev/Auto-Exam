/**
 * i18n - Internationalization System
 * Supports: English, Russian, Hebrew (RTL)
 * Stores language preference in localStorage
 */

class I18nManager {
    constructor() {
        this.currentLanguage = localStorage.getItem('language') || 'en';
        this.translations = {};
        this.supportedLanguages = ['en', 'ru', 'he'];
        this.isReady = false;
        this.readyPromise = this.init();
    }

    async init() {
        await this.loadLanguage(this.currentLanguage);
        this.isReady = true;
        return true;
    }

    /**
     * Load language translations from server
     */
    async loadLanguage(lang) {
        if (!this.supportedLanguages.includes(lang)) {
            lang = 'en';
        }

        try {
            const response = await fetch(`/api/translations/${lang}`);
            if (response.ok) {
                this.translations = await response.json();
                this.currentLanguage = lang;
                localStorage.setItem('language', lang);
                this.applyLanguageSettings();
                return true;
            }
        } catch (error) {
            console.error(`Failed to load language '${lang}':`, error);
        }
        return false;
    }

    /**
     * Get translation for key
     * @param {string} key - Translation key
     * @param {object} params - Optional parameters for interpolation
     * @returns {string} Translated text or key if not found
     */
    t(key, params = {}) {
        let text = this.translations[key] || key;

        // Simple parameter interpolation
        Object.keys(params).forEach(param => {
            text = text.replace(new RegExp(`{{${param}}}`, 'g'), params[param]);
        });

        return text;
    }

    /**
     * Apply language-specific settings to the page
     */
    applyLanguageSettings() {
        const direction = this.getDirection();
        const htmlElement = document.documentElement;

        // Set HTML direction
        htmlElement.dir = direction;
        htmlElement.lang = this.currentLanguage;

        // Set body direction
        document.body.dir = direction;

        // Update all elements with data-i18n attribute
        this.updateTranslatableElements();

        // Trigger custom event for components to react to language change
        window.dispatchEvent(new CustomEvent('languageChanged', {
            detail: { language: this.currentLanguage, direction }
        }));
    }

    /**
     * Update all elements with data-i18n attribute
     */
    updateTranslatableElements() {
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.dataset.i18n;
            const translation = this.t(key);

            if (element.tagName === 'INPUT') {
                if (element.hasAttribute('placeholder')) {
                    element.placeholder = translation;
                } else {
                    element.value = translation;
                }
            } else if (element.tagName === 'BUTTON') {
                // For buttons, always use textContent (not value)
                element.textContent = translation;
            } else if (element.tagName === 'IMG') {
                element.alt = translation;
            } else {
                element.textContent = translation;
            }
        });

        // Update title attribute
        document.querySelectorAll('[data-i18n-title]').forEach(element => {
            const key = element.dataset.i18nTitle;
            element.title = this.t(key);
        });
    }

    /**
     * Get text direction based on current language
     * @returns {string} 'ltr' or 'rtl'
     */
    getDirection() {
        return this.currentLanguage === 'he' ? 'rtl' : 'ltr';
    }

    /**
     * Get current language code
     * @returns {string}
     */
    getLanguage() {
        return this.currentLanguage;
    }

    /**
     * Get list of supported languages with display names
     * @returns {array}
     */
    getSupportedLanguages() {
        return [
            { code: 'en', name: this.t('english') },
            { code: 'ru', name: this.t('russian') },
            { code: 'he', name: this.t('hebrew') }
        ];
    }

    /**
     * Switch to language and update DOM
     * @param {string} lang - Language code
     */
    async switchLanguage(lang) {
        const success = await this.loadLanguage(lang);
        if (success) {
            this.updateTranslatableElements();
        }
        return success;
    }
}

// Global instance - expose to window
const i18n = new I18nManager();
window.i18n = i18n;

// Note: init() is async but runs automatically in constructor
// Language settings are applied via init() -> loadLanguage() -> applyLanguageSettings()

// Wait for DOM to be ready and ensure i18n is initialized
document.addEventListener('DOMContentLoaded', () => {
    // Give i18n a moment to load translations
    setTimeout(() => {
        i18n.applyLanguageSettings();
    }, 50);
});
