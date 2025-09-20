from mmu import MMU

class LruMMU(MMU):
    def __init__(self, frames):
        # Number of physical frames available
        self.frames = frames
        # Page table mapping page numbers to frame info and dirty bit
        self.page_table = {}
        # List to maintain LRU order of pages
        self.page_order = []
        # Debug mode flag
        self.debug_mode = False
        # Statistics counters
        self.disk_reads = 0
        self.disk_writes = 0
        self.page_faults = 0    

    def set_debug(self):
        self.debug_mode = True

    def reset_debug(self):
        self.debug_mode = False

    def read_memory(self, page_number):
        # Handle memory read operation
        if page_number in self.page_table:
            # Page is in memory (hit)
            if self.debug:
                print(f"Read hit: page {page_number} in frame {self.page_table[page_number]['frame']}")
        else:
            # Page fault: page not in memory
            self.page_faults += 1
            self.disk_reads += 1
            if len(self.frame_list) < self.frames:
                # Free frame available, load page
                frame_idx = len(self.frame_list)
                self.frame_list.append(page_number)
            else:
                # No free frame, evict least recently used page
                lru_page = self.page_order.pop(0)
                frame_idx = self.page_table[lru_page]['frame']
                if self.page_table[lru_page]['dirty']:
                    # Write dirty page to disk before eviction
                    self.disk_writes += 1
                    if self.debug:
                        print(f"Writing dirty page {lru_page} to disk from frame {frame_idx}")
                del self.page_table[lru_page]
                self.frame_list[frame_idx] = page_number

    def write_memory(self, page_number):
        # Handle memory write operation
        if page_number in self.page_table:
            # Page is in memory (hit), mark as dirty
            self.page_table[page_number]['dirty'] = True
            if self.debug_mode:
                print(f"Write hit: page {page_number} in frame {self.page_table[page_number]['frame']}")
        else:
            # Page fault: page not in memory
            self.page_faults += 1
            self.disk_reads += 1
            if len(self.page_order) < self.frames:
                # Free frame available, load page
                frame_idx = len(self.page_order)
                self.page_order.append(page_number)
            else:
                # No free frame, evict least recently used page
                lru_page = self.page_order.pop(0)
                frame_idx = self.page_table[lru_page]['frame']
                if self.page_table[lru_page]['dirty']:
                    # Write dirty page to disk before eviction
                    self.disk_writes += 1
                    if self.debug_mode:
                        print(f"Writing dirty page {lru_page} to disk from frame {frame_idx}")
                del self.page_table[lru_page]
                self.page_order.append(page_number)
            # Add new page to page table and mark as dirty
            self.page_table[page_number] = {'frame': frame_idx, 'dirty': True}
            if self.debug_mode:
                print(f"Page fault: loaded page {page_number} into frame {frame_idx} (write)")

    def get_total_disk_reads(self):
        return self.disk_reads

    def get_total_disk_writes(self):
        return self.disk_writes

    def get_total_page_faults(self):
        return self.page_faults
