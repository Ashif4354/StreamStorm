import { Settings } from 'lucide-react';


const NavBar = () => {

    return (
        <div>
            <nav className={`navbar`}>
                <a onClick={null} className='navbar-item'> <Settings /> Settings</a>
                {/* Other navigation items go here */}
            </nav>
        </div>
    )
}

export default NavBar;