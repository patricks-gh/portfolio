/**
 * Appends rows from A2:H49 in the current PO template
 * into the "purchase_orders" sheet, assigns a PO number based on A2 date,
 * creates a Drive folder for the PO, and ignores blank rows.
 * 
 * Now adds "Original" in column J (type column) of purchase_orders.
 */
function submitPurchaseOrder_POTemplate() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const templateSheet = ss.getActiveSheet();
  const purchaseOrdersSheet = ss.getSheetByName("purchase_orders");

  // Restrict to PO template sheets
  const sheetName = templateSheet.getName();
  if (!sheetName.startsWith("po_template_")) {
    SpreadsheetApp.getUi().alert("You can only submit from a PO template sheet.");
    return;
  }

  // Get PO creation date from A2
  const poCreationDate = templateSheet.getRange("A2").getValue();
  if (!poCreationDate || !(poCreationDate instanceof Date)) {
    SpreadsheetApp.getUi().alert("Invalid or missing PO creation date in cell A2.");
    return;
  }

  const dateKey = Utilities.formatDate(poCreationDate, Session.getScriptTimeZone(), "yyyyMMdd");
  const poPrefix = `PO-${dateKey}-`;

  // Collect data rows
  const dataRange = templateSheet.getRange("A2:H49");
  let data = dataRange.getValues();
  data = data.filter(row => row.join("").trim() !== "");
  if (data.length === 0) {
    SpreadsheetApp.getUi().alert("No valid data to submit. Please fill out at least one product row.");
    return;
  }

  // Generate PO number based on date from A2
  const existingPOs = purchaseOrdersSheet
    .getRange(2, 1, Math.max(purchaseOrdersSheet.getLastRow() - 1, 1), 1)
    .getValues()
    .flat()
    .filter(v => typeof v === "string" && v.startsWith(poPrefix));

  const todayPOs = existingPOs
    .map(v => parseInt(v.split("-").pop(), 10))
    .filter(n => !isNaN(n));

  const nextNum = todayPOs.length > 0 ? Math.max(...todayPOs) + 1 : 1;
  const newPONumber = `${poPrefix}${nextNum}`;

  // Add PO number as first column and "Original" as last (column J)
  // Columns in purchase_orders will now be:
  // A: PO#, B–I: copied data (8 cols), J: "Original"
  const output = data.map(row => [newPONumber, ...row, "Original"]);

  // Append to purchase_orders
  purchaseOrdersSheet
    .getRange(purchaseOrdersSheet.getLastRow() + 1, 1, output.length, output[0].length)
    .setValues(output);

  // Create folder under Invoices/YYYY/PO-number/
  const yearFolderName = poCreationDate.getFullYear().toString();
  const baseFolder = DriveApp.getFoldersByName("Invoices").hasNext()
    ? DriveApp.getFoldersByName("Invoices").next()
    : DriveApp.createFolder("Invoices");
  const yearFolder = baseFolder.getFoldersByName(yearFolderName).hasNext()
    ? baseFolder.getFoldersByName(yearFolderName).next()
    : baseFolder.createFolder(yearFolderName);
  const poFolder = yearFolder.createFolder(newPONumber);

  SpreadsheetApp.getUi().alert(`✅ Purchase Order ${newPONumber} submitted!\n\n📁 Folder created:\n${poFolder.getName()}`);
}
