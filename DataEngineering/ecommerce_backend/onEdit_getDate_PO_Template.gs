function onEdit_getDate_PO_Template(e) {
  try {
    const sh = e.range.getSheet();
    const sheetName = sh.getName();

    // Only run for sheets that start with "po_template_"
    if (!/^po_template_/i.test(sheetName)) return;

    const col = e.range.getColumn();
    const row = e.range.getRow();

    // Only trigger on column C (product), skip header
    if (col !== 3 || row < 2) return;

    const dateCell = sh.getRange(row, 1); // Column A
    const productValue = e.range.getValue();

    // Only fill once (don’t overwrite)
    if (productValue && !dateCell.getValue()) {
      const today = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd");
      dateCell.setValue(today);
    }

  } catch (err) {
    Logger.log("Error in onEditPODate: " + err);
  }
}
