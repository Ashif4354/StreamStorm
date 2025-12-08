import { useState } from "react";

const CodeBlock = ({ code }) => {
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(code);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className='linux-code-block-container'>
            <code className='linux-code-block'>{code}</code>
            <button className='linux-copy-button' onClick={handleCopy}>
                {copied ? '✓ Copied' : 'Copy'}
            </button>
        </div>
    );
};

const Linux = () => {

    return (
        <section className='download-section'>
            <div className='download-section-title-container'>
                <h4 className='download-section-title'>Download for Linux</h4>
            </div>
            <span className="download-note">
                <i>For Linux distributions with glibc 2.31+</i>
            </span>

            {/* Tar.gz Installation */}
            <div className='linux-install-method'>
                <h5 className='linux-method-title'>📦 Option 1: tar.gz Package</h5>
                <ol className='linux-install-list'>
                    <li>
                        <span className='linux-step-label'>Install dependencies:</span>
                        <CodeBlock code="sudo apt-get update && sudo apt-get install -y python3 python3-pyqt5 python3-pyqt5.qtwebengine python3-pyqt5.qtwebchannel libqt5webkit5 python3-xlib scrot python3-tk python3-dev" />
                    </li>
                    <li>
                        <span className='linux-step-label'>Download the package:</span>
                        <CodeBlock code="wget https://github.com/Ashif4354/StreamStorm/releases/latest/download/streamstorm.tar.gz" />
                    </li>
                    <li>
                        <span className='linux-step-label'>Extract the archive:</span>
                        <CodeBlock code="tar -xzf StreamStorm.tar.gz" />
                    </li>                    
                    <li>
                        <span className='linux-step-label'>Navigate to the directory:</span>
                        <CodeBlock code="cd StreamStorm" />
                    </li>
                    <li>
                        <span className='linux-step-label'>Make the script executable:</span>
                        <CodeBlock code="chmod +x StreamStorm-linux" />
                    </li>
                    <li>
                        <span className='linux-step-label'>Create a symbolic link:</span>
                        <CodeBlock code="sudo ln -s $PWD/StreamStorm-linux /usr/local/bin/streamstorm" />
                    </li>
                    <li>
                        <span className='linux-step-label'>Run StreamStorm:</span>
                        <CodeBlock code="streamstorm" />
                    </li>
                </ol>
            </div>

            {/* Debian Installation */}
            <div className='linux-install-method'>
                <h5 className='linux-method-title'>🐧 Option 2: Debian Package (Ubuntu/Debian)</h5>
                <ol className='linux-install-list'>
                    <li>
                        <span className='linux-step-label'>Download the .deb file:</span>
                        <CodeBlock code="wget https://github.com/Ashif4354/StreamStorm/releases/latest/download/streamstorm.deb" />
                    </li>
                    <li>
                        <span className='linux-step-label'>Install the package:</span>
                        <CodeBlock code="sudo dpkg -i ./streamstorm.deb" />
                        <p>or</p>
                        <CodeBlock code="sudo apt install ./streamstorm.deb" />
                    </li>
                    <li>
                        <span className='linux-step-label'>Run StreamStorm:</span>
                        <CodeBlock code="streamstorm" />
                        <span className='linux-step-label'>...or Start the application from the application menu</span>
                    </li>
                </ol>
            </div>

             <span className="download-note">
                <i>⚠️ Note: Linux builds currently do not support checking for new versions and auto-update functionality. We are working on adding this feature soon.</i>
            </span>
        </section>
    )
};

export default Linux
