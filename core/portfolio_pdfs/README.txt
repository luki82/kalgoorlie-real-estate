PORTFOLIO DRAWINGS
==================

1. Put your PDF drawings in this folder. Each PDF is one project, and every
   page of it is shown on the Portfolio page.

2. Name the files so they sort in the order you want, for example:
      01_Kalgoorlie_family_home.pdf
      02_Boulder_shed_and_patio.pdf
   The number only sets the order. The rest becomes the title
   ("Kalgoorlie family home").

3. Optional: add a .txt file with the same name to show a short description,
   e.g. 01_Kalgoorlie_family_home.txt

4. In PowerShell, from the core folder, run:
      python manage.py build_portfolio
   then commit and push to GitHub.

To remove a project: delete its PDF, run build_portfolio again, then push.

Before publishing, check the drawings don't show a client's name, street
address or lot details unless they have agreed to it.
