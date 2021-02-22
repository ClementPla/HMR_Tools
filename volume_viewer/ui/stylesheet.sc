
QWidget {
    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #565656, stop: 0.1 #525252, stop: 0.5 #4e4e4e, stop: 0.9 #4a4a4a, stop: 1 #464646);
    color: white;

    }
QText {
    color: white;
}

QMenuBar {
    color: white;
}

QStatusBar {
    color: white;
}

QSplitter::handle:horizontal {
   background: #1f1f1f;
   width: 2px
}

QSplitter::handle:vertical {
   background: #1f1f1f;
   height: 2px;
}

Panel {
    border-radius: 5px;
    border-style: solid;
    border: 2px;
    margin: 3px;

}

ImageProperties {
}


Panel > QComboBox {
    border-radius: 5px;
    min-width: 6em;
    color: white;
    margin: 0px;
    padding: 2px;
}

Panel > QComboBox::drop-down
{
     subcontrol-origin: padding;
     subcontrol-position: top right;
     border-left-width: 0px;
     border-left-style: solid; /* just a single line */
     border-top-right-radius: 5px; /* same radius as the QComboBox */
     border-bottom-right-radius: 5px;
     padding-left: 2px;
     padding-right: 2px;

 }

Panel > QComboBox::down-arrow {
    image: url(ui/icons/small_down_arrow.png); /* Set combobox button */
    width: 8px;
    padding: 4px;

}