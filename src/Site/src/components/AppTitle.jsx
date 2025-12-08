import { Fragment } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const AppTitle = () => {

    const pathname = usePathname();

    const titleClickHandler = () => {
        window.scrollTo(0, 0);
    }
    return (
        <Fragment>
            {
                pathname !== '/' ? (
                    <Link href="/" className="header-title-container" onClick={titleClickHandler}>
                        <span className="header-title-stream">Stream</span>
                        <span className="header-title-storm">Storm</span>
                    </Link>
                ) : (
                    <h1 className='title-heading' aria-label="StreamStorm">
                        <Link href="/" className="header-title-container" onClick={titleClickHandler}>
                            <span className="header-title-stream">Stream</span>
                            <span className="header-title-storm">Storm</span>
                        </Link>
                    </h1>
                )
            }

        </Fragment>
    )
}

export default AppTitle;