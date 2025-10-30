/**
 * Handles dependent dropdowns for po_backorders sheet.
 * When a PO Number is selected in column B, populates a product list in column C.
 * When the PO Number is cleared, removes the product dropdown.
 */
function onEdit_getProduct_PO_Reversals(e) {
  const sheet = e.range.getSheet();
  if (sheet.getName() !== "po_reversals") return; // Only for po_backorders

  const row = e.range.getRow();
  const col = e.range.getColumn();
  if (row < 2 || col !== 1) return; // Only for Col A (PO Number)

  const ss = e.source;
  const poNumber = e.value;
  const productCell = sheet.getRange(row, 4); // Column D

  // 🧹 If PO Number cleared, remove dropdown + value
  if (!poNumber) {
    productCell.clearDataValidations();
    productCell.clearContent();
    return;
  }

  // Otherwise, build dropdown for matching products
  const srcSheet = ss.getSheetByName("purchase_orders");
  const srcData = srcSheet.getDataRange().getValues();

  const poIndex = 0;      // Col A = PO Number
  const productIndex = 3; // Col D = Product Name

  const matchingProducts = srcData
    .filter((r, i) => i > 0 && r[poIndex] === poNumber && r[productIndex]) // skip header
    .map(r => r[productIndex])
    .filter((v, i, self) => self.indexOf(v) === i); // unique

  if (matchingProducts.length > 0) {
    const rule = SpreadsheetApp.newDataValidation()
      .requireValueInList(matchingProducts, true)
      .setAllowInvalid(false)
      .build();
    productCell.setDataValidation(rule);
  } else {
    // No products found, clear validations
    productCell.clearDataValidations();
    productCell.clearContent();
  }
}
