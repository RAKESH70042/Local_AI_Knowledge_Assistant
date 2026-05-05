// utils/exportChat.js

export async function exportToCSV(messages, filename = 'chat-export') {
  const rows = [
    ['Role', 'Message', 'Time', 'Attachment'],
    ...messages.map((m) => [
      m.role,
      `"${(m.content || '').replace(/"/g, '""')}"`,
      m.timestamp || '',
      m.fileName || '',
    ]),
  ];
  const csv = rows.map((r) => r.join(',')).join('\n');
  downloadBlob(new Blob([csv], { type: 'text/csv' }), `${filename}.csv`);
}

export async function exportToExcel(messages, filename = 'chat-export') {
  const XLSX = await import('xlsx');
  const wsData = [
    ['Role', 'Message', 'Time', 'Attachment'],
    ...messages.map((m) => [
      m.role,
      m.content || '',
      m.timestamp || '',
      m.fileName || '',
    ]),
  ];
  const wb = XLSX.utils.book_new();
  const ws = XLSX.utils.aoa_to_sheet(wsData);

  // Column widths
  ws['!cols'] = [{ wch: 10 }, { wch: 80 }, { wch: 20 }, { wch: 30 }];

  XLSX.utils.book_append_sheet(wb, ws, 'Chat History');
  XLSX.writeFile(wb, `${filename}.xlsx`);
}

export async function exportToDocx(messages, filename = 'chat-export') {
  const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType } = await import('docx');
  // ✅ Fix:
const FileSaver = await import('file-saver');
const saveAs = FileSaver.saveAs || FileSaver.default?.saveAs;
  const children = [
    new Paragraph({
      text: 'AI Knowledge Assistant — Chat Export',
      heading: HeadingLevel.HEADING_1,
      alignment: AlignmentType.CENTER,
      spacing: { after: 300 },
    }),
    new Paragraph({
      children: [
        new TextRun({
          text: `Exported on: ${new Date().toLocaleString()}`,
          italics: true,
          color: '888888',
          size: 20,
        }),
      ],
      spacing: { after: 400 },
    }),
  ];

  messages.forEach((msg) => {
    const isUser = msg.role === 'user';

    children.push(
      new Paragraph({
        children: [
          new TextRun({
            text: isUser ? '🧑 You' : '🤖 Assistant',
            bold: true,
            size: 24,
            color: isUser ? '2563EB' : '16A34A',
          }),
          msg.timestamp
            ? new TextRun({
                text: `  —  ${msg.timestamp}`,
                size: 18,
                color: '999999',
                italics: true,
              })
            : new TextRun(''),
        ],
        spacing: { before: 300, after: 80 },
      })
    );

    if (msg.fileName) {
      children.push(
        new Paragraph({
          children: [
            new TextRun({
              text: `📎 ${msg.fileName}`,
              italics: true,
              color: '6B7280',
              size: 20,
            }),
          ],
          spacing: { after: 60 },
        })
      );
    }

    // Split content into lines for paragraphs
    const lines = (msg.content || '').split('\n');
    lines.forEach((line) => {
      children.push(
        new Paragraph({
          children: [new TextRun({ text: line, size: 22 })],
          spacing: { after: 40 },
        })
      );
    });

    // Divider
    children.push(new Paragraph({ text: '', spacing: { after: 200 } }));
  });

  const doc = new Document({ sections: [{ children }] });
  const blob = await Packer.toBlob(doc);
  saveAs(blob, `${filename}.docx`);
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
