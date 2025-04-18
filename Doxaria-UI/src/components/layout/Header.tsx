export default function Header() {
    return (
        <header className="flex justify-between items-center container  border-b border-b-light/20">
            <h3 className="text-xl font-bold"><a href="/">Doxaria</a></h3>
            <nav className="flex gap-6 py-2">
                <a href="/" className=" text-content  p-2 rounded-md hover:bg-light/20 hover:text-light transition-colors ease-in-out duration-200  ">Home</a>
                <a href="/" className=" text-content p-2 rounded-md hover:bg-light/20 hover:text-light transition-colors ease-in-out duration-200  ">Dashboard</a>
                <a href="/Model" className=" text-content p-2 rounded-md hover:bg-light/20 hover:text-light transition-colors ease-in-out duration-200  ">Model</a>
                <a href="/" className=" text-content p-2 rounded-md hover:bg-light/20 hover:text-light transition-colors ease-in-out duration-200  ">Contact Us</a>
            </nav>
        </header>
    )
}