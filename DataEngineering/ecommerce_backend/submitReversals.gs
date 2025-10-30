function submitReversals() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  // Grab sheets
  const sourceSheet = ss.getSheetByName("po_reversals");
  const targetSheet = ss.getSheetByName("purchase_orders");
  const creditSheet = ss.getSheetByName("po_supplier_credits");

  // Safety checks
  if (!sourceSheet || !targetSheet || !creditSheet) {
    SpreadsheetApp.getUi().alert("❌ One or more sheets not found! Please check sheet names.");
    return;
  }

  const lastRow = sourceSheet.getLastRow();
  if (lastRow < 3) {
    SpreadsheetApp.getUi().alert("No data to process.");
    return;
  }

  const checkboxRange = sourceSheet.getRange(3, 1, lastRow - 2, 1); // A
  const dataRange = sourceSheet.getRange(3, 2, lastRow - 2, 9); // B–J
  const checkboxes = checkboxRange.getValues();
  const data = dataRange.getValues();

  const rowsToSubmit = [];
  const creditRows = [];

  data.forEach((row, i) => {
    if (checkboxes[i][0] === true) {
      const newRow = row.slice(); // clone B–J row

      // Store original total before reversal
      const originalTotal = row[8];

      // Reverse TOTAL (column J = index 8)
      newRow[8] = -Math.abs(row[8]);

      // Add "Reversal" marker for purchase_orders
      newRow.push("Reversal");

      rowsToSubmit.push(newRow);

      // Build supplier credit entry (B, C, I, J original value)
      const poNumber = row[0];   // Col B
      const poDate   = row[1];   // Col C
      const supplier = row[7];   // Col I
      const creditAmt = originalTotal; // Col J original (non-reversed)
      creditRows.push([poNumber, poDate, supplier, creditAmt]);

      // Clear the checkbox
      checkboxRange.getCell(i + 1, 1).setValue(false);
    }
  });

  if (rowsToSubmit.length > 0) {
    // Append to purchase_orders (A–J)
    targetSheet
      .getRange(targetSheet.getLastRow() + 1, 1, rowsToSubmit.length, 10)
      .setValues(rowsToSubmit);

    // Append to po_supplier_credits (A–D now)
    creditSheet
      .getRange(creditSheet.getLastRow() + 1, 1, creditRows.length, 4)
      .setValues(creditRows);

    SpreadsheetApp.getUi().alert("✅ Reversals submitted and credits recorded!");
  } else {
    SpreadsheetApp.getUi().alert("No rows selected.");
  }
}
