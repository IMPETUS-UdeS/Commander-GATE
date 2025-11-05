from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontMetrics
from .header import create_header_section

class HierarchySection:
    
    """
    Encapsulates the hierarchy widget area.
    Exposes:
      - widget: QWidget container
      - tree: QTreeWidget
    """
    
    def __init__(self, parent):
        self.widget = QWidget(parent)
        self.layout = QVBoxLayout(self.widget)

        self.label = create_header_section(self.widget, "Hierarchy View")
        self.layout.addWidget(self.label)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderLabels(["Hierarchy"])
        self.tree.setHeaderHidden(True)
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.tree.setIndentation(16)
        self.layout.addWidget(self.tree)
        

    def apply_font(self, fs: int):
        """
        Apply a consistent font to the Hierarchy section and adjust row height.
        Call this from MainWindow.update_font_size(size).
        """
        base = QFont("Arial", fs)
        self.widget.setFont(base)
        self.tree.setFont(base)
        self.label.setFont(QFont("Arial", fs, QFont.Weight.Bold))
        self._update_row_height(fs)

    def _update_row_height(self, fs: int):
        """
        Keep rows comfortably tall but compact.
        """
        fm = QFontMetrics(QFont("Arial", fs))
        row_h = max(22, fm.height() + 6)
        self.tree.setStyleSheet(
            f"""
            QTreeWidget::item {{ height: {row_h}px; padding: 1px 4px; }}
            """
        )
        
        
    def populate(self, node, write_to_console):
        self.tree.clear()
        
        def find_existing_item(name):
            found = self.tree.findItems(name, Qt.MatchFlag.MatchExactly, 0)
            return found[0] if found else None
        
        def add_objects_to_tree(parent_item, gate_obj):
            existing_node = find_existing_item(gate_obj.get_name())
            
            if not existing_node:
                item = QTreeWidgetItem([gate_obj.get_name()])
                item.setData(0, Qt.ItemDataRole.UserRole, gate_obj)
                
                if gate_obj.get_type() == "world":
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(0, Qt.CheckState.Checked)
                    
                if parent_item is None:
                    self.tree.addTopLevelItem(item)
                else:
                    parent_item.addChild(item)
                    
                write_to_console(f"Adding {gate_obj.get_name()} to tree.")
            else:
                write_to_console(f"Skipping duplicate: {gate_obj.get_name()}")
                item = existing_node
                
            for d in getattr(gate_obj, "daughters", []) or []:
                add_objects_to_tree(item, d)
                
        add_objects_to_tree(None, node)
            
    def set_item_enabled_recursively(self, item: QTreeWidgetItem, enabled: bool):
        color = Qt.GlobalColor.black if enabled else Qt.GlobalColor.gray
        item.setForeground(0, color)
        
        gate_obj = item.data(0, Qt.ItemDataRole.UserRole)
        if gate_obj:
            gate_obj.enabled = enabled
            
        item.setBackground(0, Qt.GlobalColor.white if enabled else Qt.GlobalColor.lightGray)
        for i in range(item.childCount()):
            child = item.child(i)
            child.setCheckState(0, Qt.CheckState.Checked if enabled else Qt.CheckState.Unchecked)
            self.set_item_enabled_recursively(child, enabled)
            
    
    def _walk(self, item, func):
        func(item)
        for i in range(item.childCount()):
            self._walk(item.child(i), func)
            
    def snapshot_state(self):
        """Return (expanded_ids, selected_id, scroll_value)."""
        expanded_ids = set()
        selected_id = None

        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            self._walk(root.child(i), lambda it: (
                expanded_ids.add(id(it.data(0, Qt.ItemDataRole.UserRole))) if it.isExpanded() else None
            ))

        current = self.tree.currentItem()
        if current:
            obj = current.data(0, Qt.ItemDataRole.UserRole)
            if obj is not None:
                selected_id = id(obj)

        vscroll = self.tree.verticalScrollBar().value()
        return expanded_ids, selected_id, vscroll
    
    
    def restore_state(self, expanded_ids, selected_id, vscroll):
        selected_item = None
        
        def apply_state(it):
            nonlocal selected_item
            obj = it.data(0, Qt.ItemDataRole.UserRole)
            if obj is None:
                return
            oid = id(obj)
            if oid in expanded_ids:
                it.setExpanded(True)
            if selected_id is not None and oid == selected_id:
                selected_item = it

        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            self._walk(root.child(i), apply_state)
            
        if selected_id is not None:
            self.tree.setCurrentItem(selected_item)
            self.tree.scrollToItem(selected_item)

        self.tree.verticalScrollBar().setValue(vscroll)
            
    
    def add_child_item(self, parent_obj, child_obj):
        """Insert a single child into the existing tree without rebuilding."""
        from PyQt6.QtWidgets import QTreeWidgetItem

        # Find parent item
        target = None
        root = self.tree.invisibleRootItem()

        def finder(it):
            nonlocal target
            obj = it.data(0, Qt.ItemDataRole.UserRole)
            if obj is parent_obj:
                target = it

        for i in range(root.childCount()):
            self._walk(root.child(i), finder)

        if target is None:
            return None  # parent not found; fall back to full repopulate

        # Create and attach
        item = QTreeWidgetItem([child_obj.get_name()])
        item.setData(0, Qt.ItemDataRole.UserRole, child_obj)
        if getattr(child_obj, "get_type", lambda: None)() == "world":
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(0, Qt.CheckState.Checked)

        target.addChild(item)
        target.setExpanded(True)
        self.tree.setCurrentItem(item)
        return item