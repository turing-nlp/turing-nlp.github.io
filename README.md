# NLP Special Interest Group - Alan Turing Institute

[![Website](https://img.shields.io/badge/Website-Live-brightgreen)](https://turing-nlp.github.io/)
[![Meetings](https://img.shields.io/badge/Meetings-Thursdays%204--5pm-blue)](https://turing-nlp.github.io/meetings.html)
[![Mailing List](https://img.shields.io/badge/Join-Mailing%20List-orange)](https://forms.office.com/Pages/ResponsePage.aspx?id=p_SVQ1XklU-Knx-672OE-fR6PcyyBV1JuragBENwKPJUMFEzUFRFVkQ4N0MxOTROTDlNN1Q5S1BJSCQlQCN0PWcu&wdLOR=cCC6B022F-A814-004B-942B-2E835A58A305)

## About

The Natural Language Processing Special Interest Group at The Alan Turing Institute brings together researchers, practitioners, and students to advance cutting-edge NLP research and its applications to social sciences.

### Research Focus Areas
- **Large Language Models & Reasoning** - LLMs, chain-of-thought, emergent capabilities
- **Evaluation & Benchmarking** - Synthetic data generation, robust evaluation frameworks  
- **Trust & Verification** - Fact-checking, rumour detection, misinformation analysis
- **Social Sciences Applications** - Computational social science and cultural analysis
- **Prompt Engineering & Alignment** - In-context learning, few-shot techniques, AI alignment

## Meetings

**📅 Schedule:** Every Thursday 4-5pm (UK time)  
**📍 Location:** Various meeting rooms at The Alan Turing Institute + Online  
**🚫 Exceptions:** Excluding 3rd Thursday each month

## Organizers

- **Anthony Hills** - Principal Organizer (QMUL & Turing Institute)
- **Maria Liakata** - Professor & Turing Fellow (QMUL & Turing Institute)  
- **Guneet Singh Kohli** - PhD Student (QMUL)
- **Yuxiang Zhou** - Postdoctoral Research Assistant (QMUL)

## Get Involved

### 🎯 Ways to Participate
- **Join our [mailing list](https://forms.office.com/Pages/ResponsePage.aspx?id=p_SVQ1XklU-Knx-672OE-fR6PcyyBV1JuragBENwKPJUMFEzUFRFVkQ4N0MxOTROTDlNN1Q5S1BJSCQlQCN0PWcu&wdLOR=cCC6B022F-A814-004B-942B-2E835A58A305)** (250+ members)
- **Attend weekly meetings** and paper discussions
- **Propose speakers** or volunteer to present your work
- **Suggest papers** for reading groups
- **Collaborate** on research projects

### 📧 Contact
**Anthony Hills** - a.r.hills [at] qmul.ac.uk

## Repository Structure

```
├── README.md                    # This file
├── index.html                   # Homepage
├── meetings.html                # Meeting schedule and abstracts
├── people.html                  # Organizers and community
├── events.html                  # Special events and workshops
├── meetings-data.json           # Meeting data (generated from Google Sheets)
├── data-processing/             # Tools for managing meeting data
│   ├── README.md               # Data processing guide
│   ├── convert_events.py       # Google Sheets → JSON converter
│   └── sample_events.csv       # Example data format
├── imgs/                       # Website images and assets
└── css/                        # Stylesheets and Bootstrap files
```

## Content Management

### 📅 Managing Meetings Data

**For Organizers:** We use Google Sheets to track meetings, then convert to JSON for the website.

1. **Update Google Sheets** with new events
2. **Export as CSV** (File → Download → CSV)  
3. **Use conversion tool**:
   ```bash
   cd data-processing/
   python convert_events.py your_spreadsheet.csv
   ```
4. **Upload generated `meetings-data.json`** to root directory

See [`data-processing/README.md`](data-processing/README.md) for detailed instructions.

### 🎨 Website Updates

- **Meetings:** Edit `meetings-data.json` (or use data processing tools)
- **Content:** Update relevant HTML files
- **Images:** Add to `imgs/` folder with appropriate naming
- **Commit & Push:** Changes auto-deploy via GitHub Pages

### 📝 Meeting Data Format

```json
{
  "date": "DD.MM.YYYY",
  "presenter": "Speaker Name",
  "presenterBio": "Optional bio...",
  "title": "Talk Title", 
  "authors": "Author et al.",
  "abstract": "Optional abstract...",
  "location": "Room Name (Alan Turing Institute) & online"
}
```

The website automatically categorizes meetings into:
- **This Week** (highlighted prominently)
- **Upcoming** (future meetings)
- **Previous** (past meetings, newest first)

## Technical Details

- **Built with:** Modern HTML5, CSS3, and JavaScript
- **Responsive Design:** Mobile-first approach
- **No Dependencies:** Self-contained with embedded CSS/JS
- **GitHub Pages:** Automatically deploys from main branch
- **Meeting Management:** JSON-based system for easy content updates

## Related Groups

We coordinate with these affiliated interest groups:
- [Media in the Digital Age](https://www.turing.ac.uk/research/interest-groups/media-digital-age)
- [Data Science for Mental Health](https://www.turing.ac.uk/research/interest-groups/data-science-mental-health)

## Contributing

To update the website:
1. **Fork this repository**
2. **Make your changes** (content, meetings data, etc.)
3. **Test locally** if possible
4. **Submit a pull request**

For meeting data updates, see the [data processing guide](data-processing/README.md).

---

**🌐 Website:** [turing-nlp.github.io](https://turing-nlp.github.io/)  
**🏛️ Official Page:** [Alan Turing Institute NLP SIG](https://www.turing.ac.uk/research/interest-groups/natural-language-processing)  
**📧 Contact:** Anthony Hills, Guneet Singh Kohli, Yuxiang Zhou, Maria Liakata