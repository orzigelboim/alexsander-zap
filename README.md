# **Website Mirroring Script for ZAP Scanning**

This repository contains scripts to create and manage a mirrored version of a website for use with **OWASP ZAP** to scan product collections effectively.

## **Overview**

The purpose of this script is to generate a static mirrored version of a website that ZAP can scan for vulnerabilities. The script retrieves product collections, converts them to an XML format, and optionally updates the index HTML file. This ensures the mirrored site stays up-to-date for accurate scanning.

## **How to Use**

### **1. Update the Website Content**
To update the mirrored website, you need to run the `toxml.py` script. Follow these steps:

1. Run the `toxml.py` script:
   ```bash
   python toxml.py
   ```

2. Enter the name of the collection(s) you wish to update. Ensure you:
   - Type the collection name **exactly** as it appears.
   - Confirm the collection by its **ID** during the process.

3. Once completed, the script will:
   - Show the number of products added or updated.
   - Indicate whether new collections were added.

### **2. Update `index.html` (if necessary)**
If the script detects that new collections have been added, you need to update the `index.html` file:

1. Run the `tohtml.py` script:
   ```bash
   python tohtml.py
   ```

2. This will regenerate the `index.html` file with the updated collections.

   > **Note**: If no new collections are added, you **do not** need to run `tohtml.py`.

### **3. Commit and Push Changes to GitHub**
After updating the mirrored website:

1. Stage and commit your changes:
   ```bash
   git commit -a -m "Meaningful description of the changes made"
   ```

   - Include meaningful comments that explain what was updated (e.g., "Updated products in Collection X" or "Added Collection Y to the index.html").

2. Push your changes to the remote repository:
   ```bash
   git push origin main
   ```

---

## **Script Workflow**

1. **toxml.py**:
   - Updates or creates XML files for the specified collections.
   - Ensures the mirrored site reflects the latest product data.
   - Reports the number of products scanned and added.

2. **tohtml.py**:
   - Regenerates the `index.html` file if new collections are added.
   - Keeps the mirrored site navigation consistent with the updated data.

---

## **Important Notes**

- **Accuracy is critical**: Ensure collection names match exactly, and confirm collections by their IDs during the process.
- **Meaningful commits**: When committing changes, always include a detailed description of what was updated.
- **Regular updates**: Run these scripts and push changes to GitHub whenever new data is added to ensure the mirrored site is current.

---
