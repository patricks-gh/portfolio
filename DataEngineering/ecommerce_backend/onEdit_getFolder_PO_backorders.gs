/**
 * Triggered automatically when a cell is edited.
 * If user selects/changes a PO number in column A (po_backorders sheet),
 * this creates or finds the corresponding folder in Drive
 * and writes the folder link in column F. If deleted, it clears the link.
 */
function onEdit_getFolder_PO_backorders(e) {
  const sheet = e.range.getSheet();
  if (sheet.getName() !== "po_backorders") return; // only run on target sheet

  const col = e.range.getColumn();
  const row = e.range.getRow();
  if (col !== 2 || row < 2) return; // only respond to dropdown in column A, rows 2+

  const poNumber = e.value;

  // If the cell is cleared (backspace or delete), remove the link in column I
  if (!poNumber) {
    sheet.getRange(row, 9).clearContent(); // Clear the content in column I (col 9)
    return; // Exit the function since there's no value to process
  }

  if (!poNumber.startsWith("PO-")) return;

  try {
    // Base folder in Drive
    const baseFolderName = "Invoices";
    const baseFolderIter = DriveApp.getFoldersByName(baseFolderName);
    if (!baseFolderIter.hasNext()) {
      SpreadsheetApp.getUi().alert(`Base folder '${baseFolderName}' not found.`);
      return;
    }
    const baseFolder = baseFolderIter.next();

    // Extract year from PO number (e.g., PO-20251025-1 → 2025)
    const match = poNumber.match(/^PO-(\d{4})(\d{2})(\d{2})-\d+$/);
    if (!match) return;
    const year = match[1];

    // Create/find the year folder
    let yearFolder;
    const yearIter = baseFolder.getFoldersByName(year);
    if (yearIter.hasNext()) {
      yearFolder = yearIter.next();
    } else {
      yearFolder = baseFolder.createFolder(year);
    }

    // Create/find PO-specific folder
    let poFolder;
    const poIter = yearFolder.getFoldersByName(poNumber);
    if (poIter.hasNext()) {
      poFolder = poIter.next();
    } else {
      poFolder = yearFolder.createFolder(poNumber);
    }

    // Write link to Column F (col 9)
    const folderUrl = poFolder.getUrl();
    sheet.getRange(row, 9).setFormula(`=HYPERLINK("${folderUrl}", "📁 Open Folder")`);

  } catch (err) {
    Logger.log("Error: " + err);
  }
}
