export default function Header() {
    return (
        <header className="flex justify-between items-center container  border-b border-b-primary/20">
            <a href="/" className=" "><img src="/images/doxaria.png" alt="heroimage"  className="lg:col-span-3 h-16"></img></a>
            <nav className="flex gap-6 ">
                <a href="/" className=" text-secondary  p-2 rounded-md hover:bg-cyan hover:text-light transition-colors ease-in-out duration-200  ">Home</a>
                <a href="/" className=" text-secondary p-2 rounded-md hover:bg-cyan hover:text-light transition-colors ease-in-out duration-200  ">Dashboard</a>
                <a href="/Model" className=" text-secondary p-2 rounded-md hover:bg-cyan hover:text-light transition-colors ease-in-out duration-200  ">Model</a>
                <a href="/AboutUs" className=" text-secondary p-2 rounded-md hover:bg-cyan hover:text-light transition-colors ease-in-out duration-200  ">About Us</a>
            </nav>
        </header>
    )
}