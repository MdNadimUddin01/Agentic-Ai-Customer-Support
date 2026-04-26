const defaultSuggestions = [
    { text: 'Track my order', icon: '📦' },
    { text: 'I need a refund', icon: '💰' },
    { text: 'Reset my password', icon: '🔐' },
    { text: 'Product is defective', icon: '⚠️' }
];

export function ChatQuickActions({
    suggestions = defaultSuggestions,
    disabled = false,
    onFill,
    onSend,
}) {
    return (
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {suggestions.map((suggestion) => (
                <div
                    key={suggestion.text}
                    style={{
                        display: 'flex',
                        border: '1px solid #e0e0e0',
                        borderRadius: '20px',
                        overflow: 'hidden',
                        opacity: disabled ? 0.5 : 1
                    }}
                >
                    <button
                        onClick={() => onFill?.(suggestion.text)}
                        disabled={disabled}
                        style={{
                            padding: '8px 12px',
                            backgroundColor: '#f5f7fa',
                            color: '#2c5aa0',
                            border: 'none',
                            borderRight: '1px solid #e0e0e0',
                            fontSize: '12px',
                            fontWeight: '500',
                            cursor: disabled ? 'not-allowed' : 'pointer'
                        }}
                    >
                        <span style={{ marginRight: '4px' }}>{suggestion.icon}</span>
                        {suggestion.text}
                    </button>
                    <button
                        onClick={() => onSend?.(suggestion.text)}
                        disabled={disabled}
                        title="Send now"
                        style={{
                            width: '34px',
                            backgroundColor: '#ffffff',
                            color: '#2c5aa0',
                            border: 'none',
                            fontSize: '14px',
                            cursor: disabled ? 'not-allowed' : 'pointer'
                        }}
                    >
                        ➤
                    </button>
                </div>
            ))}
        </div>
    );
}
