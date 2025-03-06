export default function Header() {
    return (
        <header className="flex justify-between items-center  px-9 py-4  border-b border-b-light/20">
            <h3 className="text-xl font-bold">Doxaria</h3>
            <nav className="flex gap-6 ">
                <a href="/" className=" text-content  p-2 rounded-md hover:bg-light/20 hover:text-light transition-colors ease-in-out duration-200  ">Home</a>
                <a href="/" className=" text-content p-2 rounded-md hover:bg-light/20 hover:text-light transition-colors ease-in-out duration-200  ">Dashboard</a>
                <a href="/" className=" text-content p-2 rounded-md hover:bg-light/20 hover:text-light transition-colors ease-in-out duration-200  ">Model</a>
                <a href="/" className=" text-content p-2 rounded-md hover:bg-light/20 hover:text-light transition-colors ease-in-out duration-200  ">Contact Us</a>
            </nav>
        </header>
    )
}