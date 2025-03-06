export default function Header() {
    return (
        <header className="flex justify-between items-center  px-9 py-4  border-b border-b-light/20">
            <h3 className="text-xl font-bold">Doxaria</h3>
            <nav className="flex gap-6 text-gray-500">
                <a href="/" className="hover:text-light">Home</a>
                <a href="/" className="hover:text-light">Dashboard</a>
                <a href="/" className="hover:text-light">Model</a>
                <a href="/" className="hover:text-light">Contact Us</a>
            </nav>
        </header>
    )
}