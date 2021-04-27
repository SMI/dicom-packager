// Prints a CSV of data for all docs in the dicom.series collection, filtered by the specified
// date. Usage: mongo --eval \"const date='201501'\" <script-name>.js"

if (typeof date === "undefined") {
  print("date must be passed to the script")
  quit()
}

const CONN = new Mongo()
CONN.getDB("admin").auth("...", "...")

print("PatientID,DirectoryPath,Modality,ImagesInSeries")

const DB_NAME = "dicom"
CONN.getDB(DB_NAME)
  .getCollection("series")
  .find({
    StudyDate: new RegExp("^" + date),
  })
  .forEach(function (doc) {
    // TODO(rkm 2020-10-27) Need to escape commas in some PatientIDs
    s = ""
    s += doc["PatientID"] + ","
    s += doc["header"]["DirectoryPath"] + ","
    s += doc["Modality"] + ","
    s += doc["header"]["ImagesInSeries"]
    print(s)
  })
