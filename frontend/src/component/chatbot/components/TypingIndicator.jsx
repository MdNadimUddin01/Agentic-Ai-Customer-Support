export function TypingIndicator() {
    return (
        <div
            style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 14px',
                borderRadius: '16px',
                backgroundColor: '#ffffff',
                border: '1px solid #e0e0e0',
                boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                color: '#546e7a',
                fontSize: '13px',
                fontWeight: '600'
            }}
        >
            <span>🤖</span>
            <span>Typing response...</span>
        </div>
    );
}
