/**
 * When a user edits column B (product/any key column),
 * this onEdit trigger writes the active sheet name into column A of the same row.
 */
function onEdit(e) {
  try {
    const range = e.range;
    const sh = range.getSheet();
    const sheetName = sh.getName();

    // Only respond to edits in column B (change if you want a different trigger column)
    if (range.getColumn() !== 2) return;

    // Only handle edits starting from row 2 (so header row unaffected)
    const startRow = 2;
    const editedStartRow = range.getRow();
    const numRows = range.getNumRows();

    if (editedStartRow + numRows - 1 < startRow) return;

    // For each edited row, set column A to sheetName when B is non-empty; clear A if B is cleared
    const targetRange = sh.getRange(Math.max(editedStartRow, startRow), 1, Math.min(numRows, sh.getLastRow() - startRow + 1));
    const bRange = sh.getRange(Math.max(editedStartRow, startRow), 2, Math.min(numRows, sh.getLastRow() - startRow + 1));
    const bVals = bRange.getValues();
    const out = bVals.map(function(r) {
      return [ (r[0] !== "" && r[0] !== null) ? sheetName : "" ];
    });
    targetRange.setValues(out);

  } catch (err) {
    // optional: Logger.log(err);
  }
}