import { useState, useEffect } from 'react';
import { useColorScheme } from '@mui/material/styles';
import {
    Accordion,
    AccordionSummary,
    AccordionDetails,
    TextField,
    Button,
    Alert,
    CircularProgress,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Chip,
    InputAdornment,
    IconButton
} from '@mui/material';
import { ChevronDown, Save, RotateCcw, Info, Check, Pin, Eye, EyeOff } from 'lucide-react';
import { useNotifications } from "@toolpad/core/useNotifications";
import { logEvent } from "firebase/analytics";
import * as atatus from "atatus-spa";

import { useCustomMUIProps } from '../../../../context/CustomMUIPropsContext';
import { useAppState } from '../../../../context/AppStateContext';
import { analytics } from '../../../../config/firebase';

const DEFAULT_OPENAI_URL = 'https://api.openai.com/v1';

const API_PROVIDERS = [
    {
        id: 'openai',
        name: 'OpenAI',
        hasBaseUrl: true,
        defaultBaseUrl: DEFAULT_OPENAI_URL,
        baseUrlDescription: 'For custom providers or local models.',
        hasReset: true,
        models: ['gpt-5.1', 'gpt-5-mini', 'gpt-5-nano', 'gpt-5-pro', 'gpt-5', 'gpt-4.1', 'other']
    },
    {
        id: 'anthropic',
        name: 'Anthropic',
        hasBaseUrl: false,
        hasReset: false,
        models: ['claude-sonnet-4-5', 'claude-haiku-4-5', 'claude-opus-4-5', 'other']
    },
    {
        id: 'google',
        name: 'Google',
        hasBaseUrl: false,
        hasReset: false,
        models: ['gemini-3-pro-preview', 'gemini-2.5-flash', 'gemini-2.5-flash-lite', 'gemini-2.5-pro', 'gemini-2.0-flash', 'gemini-2.0-flash-lite', 'other']
    }
];

// Validation functions
const isValidURL = (url) => {
    if (!url || url.trim() === "") return false;

    try {
        new URL(url);
        return true;
    } catch (error) {
        return false;
    }
};

const isValidApiKey = (apiKey) => {
    if (!apiKey || apiKey.trim() === "") return false;
    return apiKey.trim().length >= 10;
};

const ApiKeySection = ({ provider, expanded, onExpand, apiKeysData, onUpdateApiKey, isDefault, onSetDefault, onDefaultModelUpdated }) => {
    const { colorScheme } = useColorScheme();
    const { btnProps, inputProps } = useCustomMUIProps();
    const { hostAddress } = useAppState();
    const notifications = useNotifications();

    const [apiKey, setApiKey] = useState('');
    const [baseUrl, setBaseUrl] = useState(provider.defaultBaseUrl || '');
    const [model, setModel] = useState('');
    const [customModel, setCustomModel] = useState('');
    const [saveLoading, setSaveLoading] = useState(false);
    const [setDefaultLoading, setSetDefaultLoading] = useState(false);
    const [showApiKey, setShowApiKey] = useState(false);

    // Validation states
    const [apiKeyError, setApiKeyError] = useState(false);
    const [apiKeyHelperText, setApiKeyHelperText] = useState('');
    const [baseUrlError, setBaseUrlError] = useState(false);
    const [baseUrlHelperText, setBaseUrlHelperText] = useState('');
    const [modelError, setModelError] = useState(false);
    const [modelHelperText, setModelHelperText] = useState('');

    // Check if using custom URL (for OpenAI)
    const isCustomUrl = provider.hasBaseUrl && baseUrl.trim() !== '' && baseUrl.trim() !== DEFAULT_OPENAI_URL;

    // Check if provider is configured (has API key and model)
    const isConfigured = apiKey.trim().length >= 10 && (
        isCustomUrl ? customModel.trim() !== '' : (model !== '' && model !== 'other' || customModel.trim() !== '')
    );

    // Load data from parent when apiKeysData changes
    useEffect(() => {
        if (apiKeysData && apiKeysData[provider.id]) {
            const data = apiKeysData[provider.id];
            if (data.apiKey) setApiKey(data.apiKey);
            if (data.baseUrl) setBaseUrl(data.baseUrl);
            if (data.model) {
                // Check if model is in predefined list
                if (provider.models.includes(data.model)) {
                    setModel(data.model);
                    setCustomModel('');
                } else {
                    setModel('other');
                    setCustomModel(data.model);
                }
            }
        }
    }, [apiKeysData, provider.id, provider.models]);

    const validateInputs = () => {
        let isValid = true;

        // Validate API Key
        if (!apiKey || apiKey.trim() === "") {
            setApiKeyError(true);
            setApiKeyHelperText("API key is required.");
            isValid = false;
        } else if (!isValidApiKey(apiKey)) {
            setApiKeyError(true);
            setApiKeyHelperText("API key must be at least 10 characters.");
            isValid = false;
        } else {
            setApiKeyError(false);
            setApiKeyHelperText('');
        }

        // Validate Base URL (only for providers with baseUrl)
        if (provider.hasBaseUrl) {
            if (!baseUrl || baseUrl.trim() === "") {
                setBaseUrlError(true);
                setBaseUrlHelperText("Base URL is required.");
                isValid = false;
            } else if (!isValidURL(baseUrl)) {
                setBaseUrlError(true);
                setBaseUrlHelperText("Invalid URL format.");
                isValid = false;
            } else {
                setBaseUrlError(false);
                setBaseUrlHelperText(provider.baseUrlDescription);
            }
        }

        // Validate Model
        const finalModel = model === 'other' ? customModel : model;
        if (!isCustomUrl) {
            // Only validate model if not using custom URL
            if (!finalModel || finalModel.trim() === "") {
                setModelError(true);
                setModelHelperText("Model is required.");
                isValid = false;
            } else {
                setModelError(false);
                setModelHelperText('');
            }
        }

        return isValid;
    };

    const handleSave = async () => {
        if (!validateInputs()) return;

        const finalModel = model === 'other' ? customModel : model;

        setSaveLoading(true);
        try {
            const response = await fetch(`${hostAddress}/settings/ai/keys/${provider.id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    apiKey,
                    model: isCustomUrl ? customModel : finalModel,
                    ...(provider.hasBaseUrl && { baseUrl }),
                }),
            });

            if (response.ok) {
                const responseData = await response.json();
                const savedModel = isCustomUrl ? customModel : finalModel;
                onUpdateApiKey(provider.id, {
                    apiKey,
                    baseUrl,
                    model: savedModel
                });
                // If this is the default provider, update the default model in parent
                if (responseData.defaultModelUpdated && onDefaultModelUpdated) {
                    onDefaultModelUpdated(savedModel);
                }
                notifications.show(`${provider.name} settings saved successfully!`, {
                    severity: "success",
                });
                logEvent(analytics, "ai_api_key_save_success", { provider: provider.id });
            } else {
                throw new Error('Failed to save');
            }
        } catch (error) {
            console.error(`Failed to save ${provider.name} settings:`, error);
            notifications.show(`Failed to save ${provider.name} settings.`, {
                severity: "error",
            });
            atatus.notify(error, {}, ['ai_api_key_save_error']);
            logEvent(analytics, "ai_api_key_save_error", { provider: provider.id });
        } finally {
            setSaveLoading(false);
        }
    };

    const handleReset = () => {
        setApiKey('');
        setBaseUrl(provider.defaultBaseUrl || '');
        setModel('');
        setCustomModel('');
        setApiKeyError(false);
        setApiKeyHelperText('');
        setBaseUrlError(false);
        setBaseUrlHelperText(provider.baseUrlDescription || '');
        setModelError(false);
        setModelHelperText('');

        onUpdateApiKey(provider.id, {
            apiKey: '',
            baseUrl: provider.defaultBaseUrl || '',
            model: ''
        });

        notifications.show(`${provider.name} settings reset to default!`, {
            severity: "info",
        });
        logEvent(analytics, "ai_api_key_reset", { provider: provider.id });
    };

    const handleSetAsDefault = async () => {
        setSetDefaultLoading(true);
        const finalModel = isCustomUrl ? customModel : (model === 'other' ? customModel : model);
        const success = await onSetDefault(provider.id, finalModel, provider.hasBaseUrl ? baseUrl : null);
        setSetDefaultLoading(false);

        if (success) {
            notifications.show(`${provider.name} set as default provider!`, {
                severity: "success",
            });
            logEvent(analytics, "ai_set_default_provider_success", { provider: provider.id });
        } else {
            notifications.show(`Failed to set ${provider.name} as default.`, {
                severity: "error",
            });
            logEvent(analytics, "ai_set_default_provider_failed", { provider: provider.id });
        }
    };

    return (
        <Accordion
            expanded={expanded}
            onChange={() => onExpand(provider.id)}
            sx={{
                backgroundColor: colorScheme === 'light' ? 'var(--light-card-bg)' : 'var(--dark-gray)',
                boxShadow: 'none',
                '&:before': { display: 'none' },
                borderBottom: colorScheme === 'light' ? '1px solid var(--light-border)' : '1px solid #333333',
            }}
        >
            <AccordionSummary
                expandIcon={<ChevronDown size={16} />}
                sx={{
                    padding: '0',
                    minHeight: '48px',
                    '& .MuiAccordionSummary-content': {
                        margin: '12px 0',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                    },
                }}
            >
                <span className={`accordion-title ${colorScheme}-text`}>{provider.name}</span>
                {isDefault && (
                    <Chip
                        icon={<Check size={12} />}
                        label="Default"
                        size="small"
                        sx={{
                            height: '20px',
                            fontSize: '0.7rem',
                            backgroundColor: colorScheme === 'light' ? 'var(--light-primary-light)' : 'var(--bright-red)',
                            color: colorScheme === 'light' ? 'var(--light-primary)' : 'var(--light-text)',
                            '& .MuiChip-icon': {
                                color: 'inherit',
                                fontSize: '12px',
                            },
                        }}
                    />
                )}
            </AccordionSummary>
            <AccordionDetails sx={{ padding: '0 0 1rem 0' }}>
                <div className="api-key-form">
                    <div className="api-key-field">
                        <TextField
                            fullWidth
                            variant="outlined"
                            label="API Key"
                            placeholder="Enter your API key"
                            type={showApiKey ? "text" : "password"}
                            sx={inputProps}
                            value={apiKey}
                            error={apiKeyError}
                            helperText={apiKeyHelperText}
                            onChange={(e) => {
                                setApiKey(e.target.value);
                                setApiKeyError(false);
                                setApiKeyHelperText('');
                            }}
                            InputProps={{
                                endAdornment: (
                                    <InputAdornment position="end">
                                        <IconButton
                                            aria-label={showApiKey ? "Hide API key" : "Show API key"}
                                            onClick={() => setShowApiKey(!showApiKey)}
                                            edge="end"
                                            size="small"
                                            sx={{
                                                color: colorScheme === 'light' ? 'var(--dark-text)' : 'var(--light-text)',
                                                '&:hover': {
                                                    backgroundColor: colorScheme === 'light' ? 'var(--light-surface-hover)' : 'rgba(255,255,255,0.08)',
                                                },
                                            }}
                                        >
                                            {showApiKey ? <EyeOff size={18} /> : <Eye size={18} />}
                                        </IconButton>
                                    </InputAdornment>
                                ),
                            }}
                        />
                    </div>

                    {provider.hasBaseUrl && (
                        <div className="api-key-field">
                            <TextField
                                fullWidth
                                variant="outlined"
                                label="Base URL"
                                placeholder={provider.defaultBaseUrl}
                                sx={inputProps}
                                value={baseUrl}
                                error={baseUrlError}
                                helperText={baseUrlHelperText || provider.baseUrlDescription}
                                onChange={(e) => {
                                    setBaseUrl(e.target.value);
                                    setBaseUrlError(false);
                                    setBaseUrlHelperText(provider.baseUrlDescription);
                                }}
                            />
                        </div>
                    )}

                    {/* Model Selection */}
                    {isCustomUrl ? (
                        // For custom URLs, show text input for model
                        <div className="api-key-field">
                            <TextField
                                fullWidth
                                variant="outlined"
                                label="Model"
                                placeholder="Enter model name"
                                sx={inputProps}
                                value={customModel}
                                onChange={(e) => setCustomModel(e.target.value)}
                            />
                        </div>
                    ) : (
                        // For standard providers, show dropdown
                        <>
                            <div className="api-key-field">
                                <FormControl fullWidth sx={inputProps}>
                                    <InputLabel>Model</InputLabel>
                                    <Select
                                        value={model}
                                        label="Model"
                                        onChange={(e) => {
                                            setModel(e.target.value);
                                            setModelError(false);
                                            setModelHelperText('');
                                            if (e.target.value !== 'other') {
                                                setCustomModel('');
                                            }
                                        }}
                                        error={modelError}
                                    >
                                        {provider.models.map((m) => (
                                            <MenuItem key={m} value={m}>
                                                {m === 'other' ? 'Other (Enter manually)' : m}
                                            </MenuItem>
                                        ))}
                                    </Select>
                                    {modelHelperText && (
                                        <span className="helper-text error">{modelHelperText}</span>
                                    )}
                                </FormControl>
                            </div>

                            {model === 'other' && (
                                <div className="api-key-field">
                                    <TextField
                                        fullWidth
                                        variant="outlined"
                                        label="Custom Model"
                                        placeholder="Enter model name"
                                        sx={inputProps}
                                        value={customModel}
                                        onChange={(e) => setCustomModel(e.target.value)}
                                    />
                                </div>
                            )}
                        </>
                    )}

                    <div className="settings-button-group">
                        {provider.hasReset && (
                            <Button
                                startIcon={<RotateCcw size={16} />}
                                variant="contained"
                                onClick={handleReset}
                                disabled={saveLoading || setDefaultLoading}
                                sx={btnProps}
                            >
                                Reset
                            </Button>
                        )}

                        <Button
                            variant="contained"
                            startIcon={saveLoading ? <CircularProgress size={16} /> : <Save size={16} />}
                            onClick={handleSave}
                            disabled={saveLoading || setDefaultLoading}
                            sx={{
                                ...btnProps,
                                backgroundColor: colorScheme === 'light' ? "var(--light-primary)" : "var(--input-active-red-dark)",
                                color: "var(--light-text)",
                            }}
                        >
                            Save
                        </Button>

                        <Button
                            variant="contained"
                            startIcon={setDefaultLoading ? <CircularProgress size={16} /> : <Pin size={16} />}
                            onClick={handleSetAsDefault}
                            disabled={!isConfigured || isDefault || saveLoading || setDefaultLoading}
                            sx={{
                                ...btnProps,
                                backgroundColor: isDefault
                                    ? (colorScheme === 'light' ? 'var(--light-surface)' : 'var(--dark-gray)')
                                    : (colorScheme === 'light' ? 'var(--light-primary)' : 'var(--bright-red)'),
                                color: "var(--light-text)",
                                '&:disabled': {
                                    backgroundColor: colorScheme === 'light' ? 'var(--light-border)' : '#333333',
                                    color: colorScheme === 'light' ? 'var(--slight-dark-text)' : '#666666',
                                }
                            }}
                        >
                            {isDefault ? 'Default' : 'Set as Default'}
                        </Button>
                    </div>
                </div>
            </AccordionDetails>
        </Accordion>
    );
};

const ApiKeysSettings = ({ apiKeysData, onUpdateApiKey, isLoading, defaultProvider, onSetDefault, onDefaultModelUpdated }) => {
    const { colorScheme } = useColorScheme();
    const [expandedPanel, setExpandedPanel] = useState(null);

    const handleExpand = (panelId) => {
        setExpandedPanel(expandedPanel === panelId ? null : panelId);
    };

    return (
        <div className="settings-section">
            <h3 className={`settings-section-title ${colorScheme}-text`}>API Keys</h3>
            <p className={`settings-section-description settings-section-description-${colorScheme}`}>
                Manage API keys and model selection for GenAI providers.
            </p>

            <Alert
                severity="info"
                icon={<Info size={16} />}
                sx={{
                    marginTop: '1rem',
                    marginBottom: '1rem',
                    borderRadius: 'var(--border-radius)',
                }}
            >
                You can use the OpenAI provider section for other LLM providers that are compatible
                with the OpenAI API standard (e.g., Ollama, Mistral, Groq, OpenRouter, DeepSeek, LocalAI, etc.).
                Just manually set the Base URL, API Key, and Model.
            </Alert>

            {isLoading ? (
                <div className="settings-loading">
                    <CircularProgress size={24} />
                    <span>Loading settings...</span>
                </div>
            ) : (
                <div className="api-keys-accordion-container">
                    {API_PROVIDERS.map((provider) => (
                        <ApiKeySection
                            key={provider.id}
                            provider={provider}
                            expanded={expandedPanel === provider.id}
                            onExpand={handleExpand}
                            apiKeysData={apiKeysData}
                            onUpdateApiKey={onUpdateApiKey}
                            isDefault={defaultProvider === provider.id}
                            onSetDefault={onSetDefault}
                            onDefaultModelUpdated={onDefaultModelUpdated}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

export default ApiKeysSettings;
