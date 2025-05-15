
export default function HeroSection() {
    return(
        <section  >
            <div className="grid grid-cols-1 lg:grid-cols-5 lg:items-center gap-4 lg:gap-16 mt-20 px-9">
                <div className=" content-center lg:col-span-2  ">
                    <h3 className="text-2xl lg:text-4xl font-bold text-primary text-start leading-tight">
                        Check Our Latest Model!
                    </h3>
                    <span className="mt-3 text-md text-secondary">AI-driven image processing for smarter medical data extraction.</span>
                    <div className="mt-4 flex justify-center ">
                        <a href="/Model"
                           className=" rounded-md border-2 p-2 border-primary hover:border-cyan hover:bg-light hover:text-dark w-1/3 text-center">
                            Click HERE!
                        </a>
                    </div>
                </div>
                <img src="/images/DoxariaHero.webp" alt="heroimage" className="lg:col-span-3  "></img>

            </div>
        </section>
    )
}