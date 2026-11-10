# Technology / テクノロジー

## Computing foundations
- **Turing machine / チューリングマシン** — a 1936 thought experiment that defined what "computable" means, before real computers existed → philosophy: limits of knowledge
- **Halting problem / 停止問題** — provably, no program can decide for every program whether it halts → Gödel's incompleteness
- **Von Neumann architecture** — storing programs in the same memory as data; still the shape of nearly every computer
- **Boolean logic** — George Boole (1854) turned logic into algebra; Claude Shannon's 1937 master's thesis linked it to circuits
- **Information theory / 情報理論** — Shannon (1948) defined the *bit* and the limits of compression and communication → entropy in physics
- **Moore's law** — transistor counts doubling ~every 2 years; an observation and an industry target, not a law of nature
- **Big-O notation / 計算量** — why an algorithm that is "fast enough" on 1,000 items can die on 1,000,000

## Software & engineering
- **Unix philosophy** — "do one thing well", small tools connected by pipes → Lego, microservices
- **Git** — written by Linus Torvalds in about 10 days in 2005 after a licensing dispute over BitKeeper
- **The Mythical Man-Month** — "adding people to a late software project makes it later" (Brooks's law)
- **Conway's law** — systems mirror the communication structure of the organizations that build them
- **Technical debt / 技術的負債** — Ward Cunningham's metaphor (1992): shortcuts accrue interest
- **Kanban & Lean in software** — borrowed directly from the Toyota Production System → japan.md: カイゼン
- **Ruby** — created by Yukihiro "Matz" Matsumoto (まつもとゆきひろ), released 1995, designed for "programmer happiness"
- **Open source** — Linux, Apache, Wikipedia-style collaboration; why companies give code away

## Networks & the internet
- **Packet switching** — Paul Baran and Donald Davies independently invented it in the 1960s
- **TCP/IP** — Vint Cerf & Bob Kahn (1974); flow control and congestion control as "polite sharing" of a road
- **DNS** — the internet's phone book; a handful of root server identities (13 names) served by 1,000+ machines via anycast
- **The World Wide Web** — Tim Berners-Lee at CERN, 1989; first website still reachable (info.cern.ch)
- **i-mode / iモード** — NTT Docomo's 1999 mobile internet; Japan had mobile web, emoji and mobile payments years ahead → japan.md: 絵文字
- **Emoji / 絵文字** — Shigetaka Kurita (栗田穣崇) designed an early influential 176-emoji set for i-mode (1999); now in MoMA's collection
- **Undersea cables / 海底ケーブル** — ~99% of intercontinental data travels on seabed cables, not satellites
- **CAP theorem** — in a network partition, a distributed system must choose consistency or availability

## AI & data
- **Dartmouth workshop (1956)** — where the term "artificial intelligence" was coined
- **AI winters** — hype cycles of the 1970s and late 1980s; Japan's Fifth Generation Computer project (1982–1992) is part of the story
- **Neural networks & backpropagation** — old ideas (1980s) that became powerful with GPUs and big data (~2012, AlexNet)
- **Transformers** — "Attention Is All You Need" (2017); the architecture behind modern LLMs
- **Neocognitron** — Kunihiko Fukushima (福島邦彦, 1979–80), a precursor of convolutional neural networks
- **Overfitting / 過学習** — memorizing instead of understanding → education, superstition
- **Goodhart's law** — "when a measure becomes a target, it ceases to be a good measure" → economics, AI reward hacking

## Hardware & industry
- **Semiconductor supply chain** — ASML (Netherlands) EUV machines, TSMC (Taiwan) fabs; Japan supplies key materials (photoresists, silicon wafers)
- **Rapidus** — Japan's effort to build leading-edge (2nm) chip manufacturing in Hokkaido
- **Walkman (1979)** — Sony made music personal and portable → arts: how listening changed
- **QR code (1994)** — invented by Masahiro Hara (原昌宏) at Denso Wave, inspired by the game of Go; patent deliberately not enforced
- **Shinkansen ATC / 新幹線** — automatic train control; the Tokaido line's average delay is typically under a minute → japan.md
- **Quantum computing** — qubits, superposition; useful for specific problems, not a "faster everything" machine
- **Cryptography / 暗号** — public-key crypto (Diffie–Hellman 1976, RSA 1977); Enigma and Bletchley Park → history

## Hooks (surprising facts)
- The first "computer bug" logged (1947) was a real moth taped into the Harvard Mark II logbook — though "bug" was already engineering slang.
- Ada Lovelace published what is often called the first computer program in 1843, for a machine never built.
- The Apollo Guidance Computer had about 4 KB of RAM (2048 words); its software was woven as "core rope memory", partly by hand.
- Japan's calculator war (電卓戦争) of the 1960s–70s led Japanese firm Busicom to commission Intel's 4004 (1971), the first commercial microprocessor.
