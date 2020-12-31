use super::cept::*;
use super::pages::*;

pub struct HistoricPageGenerator {
    pub page: Page,
}

impl HistoricPageGenerator {
    pub fn new(page: Page) -> Self {
        Self {
            page: page,
        }
    }

    pub fn create(pageid: &str) -> Self {
        if pageid == "8a" {
            Self::create_historic_main_page()
        } else if pageid == "10a" || pageid == "11a" || pageid == "12a" {
            create_historic_overview(pageid[0..2].parse().unwrap(), 0).unwrap()
        } else {
            panic!();
        }
    }

    fn create_title(&mut self, title: &str) {
        self.page.cept.set_cursor(2, 1);
        self.page.cept.set_palette(1);
        self.page.cept.set_screen_bg_color_simple(4);
        self.page.cept.add_raw(
            &[0x1b, 0x28, 0x40,       // load G0 into G0
             0x0f]                   // G0 into left charset
        );
        self.page.cept.parallel_mode();
        self.page.cept.set_palette(0);
        self.page.cept.code_9e();
        self.page.cept.set_line_bg_color_simple(4);
        self.page.cept.add_raw(b"\n");
        self.page.cept.set_line_bg_color_simple(4);
        self.page.cept.set_palette(1);
        self.page.cept.double_height();
        self.page.cept.add_raw(b"\r");
        self.page.cept.add_str(title);
        self.page.cept.add_raw(b"\n\r");
        self.page.cept.set_palette(0);
        self.page.cept.normal_size();
        self.page.cept.code_9e();
        self.page.cept.set_fg_color_simple(7);
    }

	fn footer(&mut self, left: &str, right: Option<&str>) {
		self.page.cept.set_cursor(23, 1);
		self.page.cept.set_palette(0);
		self.page.cept.set_line_bg_color_simple(4);
		self.page.cept.add_str(left);

		if let Some(right) = right {
            self.page.cept.set_cursor(23, 41 - right.len() as u8);
            self.page.cept.add_str(right);
        }
    }

    fn historic_line(&mut self, page: (&str, &str), index: i32) {
        let link = historic_pretty_link_from_str(page.0);
        let mut s = page.1.to_string();
        s += " ";
        s += &link;
        while s.chars().count() < 38 {
            s.push('.');
        }
        self.page.cept.add_str(&s);
        self.page.cept.add_str(&index.to_string());
    }


	pub fn create_historic_main_page() -> Self {
        let meta = Meta {
            publisher_name: Some("!BTX".to_owned()),
            clear_screen: true,
            cls2: false,
            parallel_mode: false,
            links: vec![
        		("0".to_owned(), "0".to_owned()),
				("10".to_owned(), "710".to_owned()),
				("11".to_owned(), "711".to_owned()),
				("#".to_owned(), "711".to_owned()),
            ],
            publisher_color: 7,
            inputs: None,
		};

        let mut generator = Self::new(Page::new(meta));
		generator.create_title("Historische Seiten");
		generator.page.cept.add_raw(b"\r\n");
		generator.page.cept.add_str(
			"Nur wenige hundert der mehreren hundert-\
			tausend BTX-Seiten sind überliefert.\n\
			Die meisten entstammen dem Demomodus von\
			Software-BTX-Decoderprogrammen.\n\
			\n\
			1988: C64 BTX Demo (Input 64 12/88)...--\
			1989: Amiga BTX Terminal..............10\
			1989: C64 BTX Demo (64'er 1/90).......--\
			1991: BTX-VTX Manager v1.2............--\
			1993: PC online 1&1...................11\
			1994: MacBTX 1&1......................--\
			1995: BTXTEST.........................--\
			1996: RUN_ME..........................--\
			\n\
			Da historische Seiten erst angepaßt wer-\
			den müssen, um nutzbar zu sein, sind\n\
			noch nicht alle Sammlungen verfügbar."
			//XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
		);

		generator.footer("0 Zurück", None);
        generator
    }
}


pub fn create_historic_overview(collection: i32, index: i32) -> Option<HistoricPageGenerator> {
    let name;
    let description;
    let distribution;
    let start_page;
    let pages;

    if collection == 10 {
        name = "Amiga Demo";
        description =
            "Der Amiga BTX Software-Decoder wurde mit\
            Dumps von 113 BTX-Seiten aus 32\n\
            Programmen ausgeliefert, sowie 56 eigens\
            gestalteten Seiten zum Thema BTX.\n\
            Die Seiten stammen vom April 1989.";
        distribution = vec!(9, 17);

        start_page = Some(("20096/1", "Amiga Demo Startseite"));

        pages = vec!(
            ("1050", "Btx-Telex"),
            ("1188", "Teleauskunft"),
            ("1692", "Cityruf"),
            ("20000", "Deutsche Bundespost"),
            ("20096", "Commodore"),
            ("20511/223", "Kölner Stadtanzeiger"),
            ("21212", "Verbraucher-Zentrale NRW"),
            ("25800/0000", "Deutsche Bundesbahn"),
            ("30003", "Formel Eins"),
            ("30711", "Btx Südwest Datenbank GmbH"),
            ("33033", "Eden"),
            ("34034", "Frankfurter Allg. Zeitung"),
            ("34344", "Neue Mediengesellschaft Ulm"),
            ("35853", "ABIDA GmbH"),
            ("40040/200", "Axel Springer Verlag"),
            ("44479", "DIMDI"),
            ("50257", "Computerwelt Btx-Info-Dienst"),
            ("54004/04", "ÖVA Versicherungen"),
            ("57575", "Lotto Toto"),
            ("64064", "Markt & Technik"),
            ("65432/0", "ADAC"),
            ("67007", "Rheinpfalz Verlag/Druckerei"),
            ("201474/75", "Rhein-Neckar-Zeitung"),
//			("208585", "eba Pressebüro und Verlag [BROKEN]"),
            ("208888", "Neue Mediengesellschaft Ulm"),
            ("402060", "AUTO & BTX WOLFSBURG"),
            ("50707545", "CHIP Magazin"),
            ("86553222", "Chaos Computer Club"),
            ("505050035", "Steinfels Sprachreisen"),
            ("920492040092", "Wolfgang Fritsch (BHP)"),
        );
    } else if collection == 11 {
        name = "PC online 1&1";
        description =
            "Der PC online 1&1 Decoder wurde mit\n\
            von 25 BTX-Seiten aus 15 Programmen\n\
            ausgeliefert. Die Seiten stammen vom\n\
            November 1993.";
        distribution = vec!(12);

        start_page = None;

        pages = vec!(
            ("00000/88", "Teleauskunft"),
            ("00000/1188", "Mitteilungsdienst"),
            ("20111/1", "Vobis Microcomputer AG"),
            ("20111/11020", "- Übersicht 486"),
            ("20111/1102030", "- 486 DX-50 "),
            ("20111/110203010", "- 486 DX-50 Details"),
            ("21199", "Microsoft"),
            ("21199/1362", "- Produkte"),
            ("25800", "Deutsche Bundesbahn"),
            ("28000/101", "Postbank"),
            ("34561/10", "1&1 Telekommunkation"),
            ("34561/99", "- Forum [a-b]"),
            ("37107/2154", "WDR Computer-Club"),
            ("46801/8149999999", "Handelsblatt"),
            ("49498/0004902", "bhv Computerbücher"),
            ("49498/000490201", "- Neuheiten"),
            ("50000", "Deutsche Lufthansa"),
            ("52800", "IBM Deutschland"),
            ("52800/03", "- IBM Personal Systeme"),
            ("52800/31", "- HelpClubShop [a-c]"),
            ("58587/003", " ITZ Schulungen"),
            ("69010", "Deutscher Ind. Handelstag"),
            ("353535/00", "START Tourismus"),
            ("353535/01240", "- Veranstalter"),
            ("353535/01640", "- Reiseinformationen"),
        );
    } else {
        return None;
    }

    let mut start_with = 0;
    if index != 0 {
        for i in 0..index as usize {
            if i >= distribution.len() {
                return None;
            }
            start_with += distribution[i];
        }
    }


    let mut links = vec!(
        ("0".to_owned(), "78".to_owned()),
    );
    if let Some(start_page) = start_page {
        links.push(("10".to_owned(), historic_link_from_str(start_page.0)));
    }
    let mut i = 20;
    for page in &pages {
        links.push((i.to_string(), historic_link_from_str(page.0)));
        i += 1
    }

    let meta = Meta {
        publisher_name: Some("!BTX".to_owned()),
        clear_screen: true,
        cls2: false,
        parallel_mode: false,
        links: links,
        publisher_color: 7,
        inputs: None,
    };

    let mut generator = HistoricPageGenerator::new(Page::new(meta));

    // sys.stderr.write("meta: " + pprint.pformat(meta) + "\n")

    let mut cept = Cept::new();
    let mut t = "Historische Seiten: ".to_owned();
    t += name;
    generator.create_title(&t);
    cept.add_str("\r\n");

    if index == 0 {
        cept.add_str(description);
        cept.add_str("\r\n\n");
        if let Some(start_page) = start_page {
            generator.historic_line(start_page, 10);
            cept.add_str("\n")
        }
    }

    let end = if index as usize >= distribution.len() {
        pages.len()
    } else {
        start_with + distribution[index as usize]
    };
    for i in start_with..end {
        generator.historic_line(pages[i], i as i32 + 20);
    }

    let right = if (index as usize) < distribution.len() { Some("Weiter #") } else { None };
    generator.footer("0 Zurück", right);
    // cept.compress();

    Some(generator)
}

fn historic_link_from_str(s: &str) -> String {
    s.replace("/", "")
}

fn historic_pretty_link_from_str(s: &str) -> String {
    let split: Vec<&str> = s.split("/").collect();
    let s = if split[0] == "00000" {
        split[1]
    } else {
        split[0]
    };
    let mut res = "(*".to_owned();
    res += s;
    res += "#)";
    res
}
