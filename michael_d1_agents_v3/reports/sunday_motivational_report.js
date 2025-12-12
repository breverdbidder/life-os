/**
 * Michael Shapira D1 Pathway - Sunday Motivational Report Generator
 * ================================================================
 * Generates weekly motivational DOCX report with:
 * - Performance tracking vs D1 standards
 * - Week's accomplishments
 * - Goals for upcoming week
 * - Inspirational content
 * 
 * Author: Everest Capital USA / Life OS
 */

const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, 
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        ShadingType, PageNumber, LevelFormat } = require('docx');
const fs = require('fs');

// Michael's Profile
const MICHAEL_PROFILE = {
    name: "Michael Shapira",
    graduation: 2027,
    school: "Satellite Beach High School",
    currentTimes: {
        "50 Free": { time: "23.22", seconds: 23.22 },
        "100 Free": { time: "50.82", seconds: 50.82 },
        "100 Fly": { time: "57.21", seconds: 57.21 },
        "100 Back": { time: "1:01.62", seconds: 61.62 }
    },
    targetSchools: [
        { name: "University of Florida", conference: "SEC", tier: 1 },
        { name: "Florida State University", conference: "ACC", tier: 1 },
        { name: "University of Miami", conference: "ACC", tier: 1 }
    ]
};

// D1 Standards
const D1_STANDARDS = {
    tier_1: {
        "50 Free": { walkOn: 21.5, recruited: 20.5, scholarship: 19.5 },
        "100 Free": { walkOn: 47.0, recruited: 45.5, scholarship: 44.0 },
        "100 Fly": { walkOn: 51.0, recruited: 49.5, scholarship: 48.0 },
        "100 Back": { walkOn: 52.0, recruited: 50.5, scholarship: 49.0 }
    }
};

// Inspirational quotes for swimmers
const QUOTES = [
    { text: "The water is your friend. You don't have to fight with water, just share the same spirit as the water, and it will help you move.", author: "Alexander Popov" },
    { text: "Set your goals high, and don't stop till you get there.", author: "Bo Jackson" },
    { text: "I think goals should never be easy, they should force you to work, even if they are uncomfortable at the time.", author: "Michael Phelps" },
    { text: "The only person you are destined to become is the person you decide to be.", author: "Ralph Waldo Emerson" },
    { text: "Success is no accident. It is hard work, perseverance, learning, studying, sacrifice.", author: "Pelé" },
    { text: "Pain is temporary. Quitting lasts forever.", author: "Lance Armstrong" },
    { text: "The harder the battle, the sweeter the victory.", author: "Les Brown" }
];

function getRandomQuote() {
    return QUOTES[Math.floor(Math.random() * QUOTES.length)];
}

function formatDate(date) {
    return date.toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
}

function getWeekNumber(date) {
    const startOfYear = new Date(date.getFullYear(), 0, 1);
    const diff = date - startOfYear;
    const oneWeek = 604800000;
    return Math.ceil((diff + startOfYear.getDay() * 86400000) / oneWeek);
}

function calculateGap(current, target) {
    const gap = current - target;
    if (gap <= 0) return { status: "ACHIEVED ✓", gap: 0, color: "00AA00" };
    if (gap < 1) return { status: "CLOSE", gap: gap.toFixed(2), color: "FFA500" };
    if (gap < 3) return { status: "IN REACH", gap: gap.toFixed(2), color: "0066CC" };
    return { status: "BUILDING", gap: gap.toFixed(2), color: "666666" };
}

async function generateSundayReport(weekData = {}) {
    const today = new Date();
    const weekNum = getWeekNumber(today);
    const quote = getRandomQuote();
    
    // Calculate days until graduation (May 2027)
    const graduationDate = new Date(2027, 4, 15);
    const daysUntilGraduation = Math.ceil((graduationDate - today) / (1000 * 60 * 60 * 24));
    const weeksUntilGraduation = Math.ceil(daysUntilGraduation / 7);
    
    // Table borders
    const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
    const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };
    
    const doc = new Document({
        styles: {
            default: { document: { run: { font: "Arial", size: 24 } } },
            paragraphStyles: [
                { id: "Title", name: "Title", basedOn: "Normal",
                  run: { size: 48, bold: true, color: "1E3A5F", font: "Arial" },
                  paragraph: { spacing: { before: 0, after: 200 }, alignment: AlignmentType.CENTER } },
                { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
                  run: { size: 32, bold: true, color: "1E3A5F", font: "Arial" },
                  paragraph: { spacing: { before: 300, after: 200 }, outlineLevel: 0 } },
                { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
                  run: { size: 26, bold: true, color: "2E5A8F", font: "Arial" },
                  paragraph: { spacing: { before: 200, after: 150 }, outlineLevel: 1 } }
            ]
        },
        numbering: {
            config: [
                { reference: "bullet-goals",
                  levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
                { reference: "bullet-accomplishments",
                  levels: [{ level: 0, format: LevelFormat.BULLET, text: "✓", alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }
            ]
        },
        sections: [{
            properties: {
                page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } }
            },
            headers: {
                default: new Header({ children: [new Paragraph({
                    alignment: AlignmentType.RIGHT,
                    children: [
                        new TextRun({ text: "Michael Shapira D1 Pathway | ", size: 18, color: "666666" }),
                        new TextRun({ text: "Week " + weekNum, size: 18, bold: true, color: "1E3A5F" })
                    ]
                })] })
            },
            footers: {
                default: new Footer({ children: [new Paragraph({
                    alignment: AlignmentType.CENTER,
                    children: [
                        new TextRun({ text: "Page ", size: 18 }),
                        new TextRun({ children: [PageNumber.CURRENT], size: 18 }),
                        new TextRun({ text: " | Everest Capital USA / Life OS", size: 18, color: "666666" })
                    ]
                })] })
            },
            children: [
                // Title
                new Paragraph({ heading: HeadingLevel.TITLE,
                    children: [new TextRun("🏊 Sunday Motivation Report")] }),
                new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
                    children: [new TextRun({ text: formatDate(today), size: 22, color: "666666" })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
                    children: [new TextRun({ text: `${daysUntilGraduation} days (${weeksUntilGraduation} weeks) until graduation`, size: 22, bold: true, color: "1E3A5F" })] }),
                
                // Inspirational Quote
                new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("💪 This Week's Inspiration")] }),
                new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200, after: 100 },
                    indent: { left: 720, right: 720 },
                    children: [new TextRun({ text: `"${quote.text}"`, italics: true, size: 26, color: "333333" })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
                    children: [new TextRun({ text: `— ${quote.author}`, size: 22, color: "666666" })] }),
                
                // Current Times vs Standards
                new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("📊 D1 Progress Tracker")] }),
                new Paragraph({ spacing: { after: 200 },
                    children: [new TextRun({ text: "Your current times vs. Tier 1 D1 recruiting standards:", size: 22 })] }),
                
                // Progress Table
                new Table({
                    columnWidths: [2000, 1800, 1800, 1800, 1960],
                    rows: [
                        new TableRow({
                            tableHeader: true,
                            children: [
                                new TableCell({ borders: cellBorders, width: { size: 2000, type: WidthType.DXA },
                                    shading: { fill: "1E3A5F", type: ShadingType.CLEAR },
                                    children: [new Paragraph({ alignment: AlignmentType.CENTER,
                                        children: [new TextRun({ text: "Event", bold: true, color: "FFFFFF", size: 22 })] })] }),
                                new TableCell({ borders: cellBorders, width: { size: 1800, type: WidthType.DXA },
                                    shading: { fill: "1E3A5F", type: ShadingType.CLEAR },
                                    children: [new Paragraph({ alignment: AlignmentType.CENTER,
                                        children: [new TextRun({ text: "Your Time", bold: true, color: "FFFFFF", size: 22 })] })] }),
                                new TableCell({ borders: cellBorders, width: { size: 1800, type: WidthType.DXA },
                                    shading: { fill: "1E3A5F", type: ShadingType.CLEAR },
                                    children: [new Paragraph({ alignment: AlignmentType.CENTER,
                                        children: [new TextRun({ text: "Walk-On", bold: true, color: "FFFFFF", size: 22 })] })] }),
                                new TableCell({ borders: cellBorders, width: { size: 1800, type: WidthType.DXA },
                                    shading: { fill: "1E3A5F", type: ShadingType.CLEAR },
                                    children: [new Paragraph({ alignment: AlignmentType.CENTER,
                                        children: [new TextRun({ text: "Recruited", bold: true, color: "FFFFFF", size: 22 })] })] }),
                                new TableCell({ borders: cellBorders, width: { size: 1960, type: WidthType.DXA },
                                    shading: { fill: "1E3A5F", type: ShadingType.CLEAR },
                                    children: [new Paragraph({ alignment: AlignmentType.CENTER,
                                        children: [new TextRun({ text: "Gap to Goal", bold: true, color: "FFFFFF", size: 22 })] })] })
                            ]
                        }),
                        ...Object.entries(MICHAEL_PROFILE.currentTimes).map(([event, data]) => {
                            const standards = D1_STANDARDS.tier_1[event] || {};
                            const gapInfo = calculateGap(data.seconds, standards.walkOn || 99);
                            return new TableRow({
                                children: [
                                    new TableCell({ borders: cellBorders, width: { size: 2000, type: WidthType.DXA },
                                        children: [new Paragraph({ children: [new TextRun({ text: event, bold: true, size: 22 })] })] }),
                                    new TableCell({ borders: cellBorders, width: { size: 1800, type: WidthType.DXA },
                                        children: [new Paragraph({ alignment: AlignmentType.CENTER,
                                            children: [new TextRun({ text: data.time, size: 22, bold: true })] })] }),
                                    new TableCell({ borders: cellBorders, width: { size: 1800, type: WidthType.DXA },
                                        children: [new Paragraph({ alignment: AlignmentType.CENTER,
                                            children: [new TextRun({ text: standards.walkOn?.toFixed(1) || "—", size: 22 })] })] }),
                                    new TableCell({ borders: cellBorders, width: { size: 1800, type: WidthType.DXA },
                                        children: [new Paragraph({ alignment: AlignmentType.CENTER,
                                            children: [new TextRun({ text: standards.recruited?.toFixed(1) || "—", size: 22 })] })] }),
                                    new TableCell({ borders: cellBorders, width: { size: 1960, type: WidthType.DXA },
                                        shading: { fill: gapInfo.color === "00AA00" ? "E8F5E9" : "FFF8E1", type: ShadingType.CLEAR },
                                        children: [new Paragraph({ alignment: AlignmentType.CENTER,
                                            children: [new TextRun({ text: gapInfo.gap > 0 ? `-${gapInfo.gap}s` : gapInfo.status, size: 22, color: gapInfo.color })] })] })
                                ]
                            });
                        })
                    ]
                }),
                
                // This Week's Goals
                new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 400 },
                    children: [new TextRun("🎯 This Week's Goals")] }),
                ...(weekData.goals || [
                    "Complete all scheduled practices with 100% effort",
                    "Focus on underwater dolphin kicks off every wall",
                    "Maintain keto diet Monday-Thursday for energy optimization",
                    "Get 8+ hours sleep each night",
                    "Review race footage from last meet"
                ]).map(goal => new Paragraph({
                    numbering: { reference: "bullet-goals", level: 0 },
                    children: [new TextRun({ text: goal, size: 22 })]
                })),
                
                // Last Week's Accomplishments
                new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 400 },
                    children: [new TextRun("✅ Last Week's Wins")] }),
                ...(weekData.accomplishments || [
                    "Completed all 6 practices",
                    "Maintained nutrition plan",
                    "Got adequate rest before weekend meet"
                ]).map(item => new Paragraph({
                    numbering: { reference: "bullet-accomplishments", level: 0 },
                    children: [new TextRun({ text: item, size: 22 })]
                })),
                
                // Target Schools Update
                new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 400 },
                    children: [new TextRun("🏫 Target Schools")] }),
                new Table({
                    columnWidths: [4680, 2340, 2340],
                    rows: [
                        new TableRow({
                            tableHeader: true,
                            children: [
                                new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA },
                                    shading: { fill: "2E5A8F", type: ShadingType.CLEAR },
                                    children: [new Paragraph({ children: [new TextRun({ text: "School", bold: true, color: "FFFFFF", size: 22 })] })] }),
                                new TableCell({ borders: cellBorders, width: { size: 2340, type: WidthType.DXA },
                                    shading: { fill: "2E5A8F", type: ShadingType.CLEAR },
                                    children: [new Paragraph({ alignment: AlignmentType.CENTER,
                                        children: [new TextRun({ text: "Conference", bold: true, color: "FFFFFF", size: 22 })] })] }),
                                new TableCell({ borders: cellBorders, width: { size: 2340, type: WidthType.DXA },
                                    shading: { fill: "2E5A8F", type: ShadingType.CLEAR },
                                    children: [new Paragraph({ alignment: AlignmentType.CENTER,
                                        children: [new TextRun({ text: "Status", bold: true, color: "FFFFFF", size: 22 })] })] })
                            ]
                        }),
                        ...MICHAEL_PROFILE.targetSchools.map(school => new TableRow({
                            children: [
                                new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA },
                                    children: [new Paragraph({ children: [new TextRun({ text: school.name, size: 22 })] })] }),
                                new TableCell({ borders: cellBorders, width: { size: 2340, type: WidthType.DXA },
                                    children: [new Paragraph({ alignment: AlignmentType.CENTER,
                                        children: [new TextRun({ text: school.conference, size: 22 })] })] }),
                                new TableCell({ borders: cellBorders, width: { size: 2340, type: WidthType.DXA },
                                    children: [new Paragraph({ alignment: AlignmentType.CENTER,
                                        children: [new TextRun({ text: "Researching", size: 22, color: "0066CC" })] })] })
                            ]
                        }))
                    ]
                }),
                
                // Closing Message
                new Paragraph({ spacing: { before: 600 }, alignment: AlignmentType.CENTER,
                    children: [new TextRun({ text: "Keep pushing, Michael! Every practice counts. 🏊‍♂️", size: 26, bold: true, color: "1E3A5F" })] }),
                new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200 },
                    children: [new TextRun({ text: "Your D1 dream is within reach.", size: 22, italics: true, color: "666666" })] })
            ]
        }]
    });
    
    const buffer = await Packer.toBuffer(doc);
    const filename = `michael_sunday_report_week${weekNum}_${today.toISOString().split('T')[0]}.docx`;
    const outputPath = process.env.OUTPUT_PATH || '/mnt/user-data/outputs';
    const fullPath = `${outputPath}/${filename}`;
    
    fs.writeFileSync(fullPath, buffer);
    console.log(`✅ Report generated: ${fullPath}`);
    
    return fullPath;
}

// Run if called directly
if (require.main === module) {
    generateSundayReport().then(path => {
        console.log(`Report saved to: ${path}`);
    }).catch(err => {
        console.error('Error generating report:', err);
        process.exit(1);
    });
}

module.exports = { generateSundayReport, MICHAEL_PROFILE, D1_STANDARDS };
