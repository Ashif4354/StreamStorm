import { useColorScheme } from "@mui/material";
import { MessageSquare } from "lucide-react";

const MessagesConfig = (props) => {
    const { messages } = props
    const { colorScheme } = useColorScheme();

    return (
        <div className='messages-config-container'>
            <div className='messages-container-top'>
                <div
                    className='text-based-config-icon-container'
                    style={{
                        color: colorScheme === "dark" ? "var(--slight-light-text)" : "var(--slight-dark-text)",
                    }}
                >
                    <MessageSquare size={16} />
                </div>

                <div
                    className='text-based-config-title-container'
                    style={{
                        color: colorScheme === "dark" ? "var(--slight-light-text)" : "var(--slight-dark-text)",
                        fontSize: '0.875rem',
                        flex: 1
                    }}
                >
                    Messages
                </div>
            </div>

            <div
                className={`messages-container ${colorScheme}-bordered-container`}
                style={{
                    color: colorScheme === "dark" ? "var(--light-text)" : "var(--dark-text)",
                    fontSize: '0.875rem'
                }}
            >
                {
                    messages.map((message, index) => (
                        <div key={index}>
                            {message}
                        </div>
                    ))
                }
            </div>
        </div>
    );
}

export default MessagesConfig