from mmu import MMU

class LruMMU(MMU):
    def __init__(self, frames):
        # Number of physical frames available
        self.frames = frames
        # Page table mapping page numbers to frame info and dirty bit
        self.page_table = {}
        # List to maintain LRU order of pages
        self.page_order = []
        # Frame index -> page (None means free)
        self.frame_list = []
        # Debug flag
        self.debug_mode = False
        # Statistics counters
        self.disk_reads = 0
        self.disk_writes = 0
        self.page_faults = 0    

    def set_debug(self):
        self.debug_mode = True

    def reset_debug(self):
        self.debug_mode = False

    # ---------- core ops ----------
    def read_memory(self, page_number):
        # Handle memory read operation
        if page_number in self.page_table:
            # hit: update recency
            self._touch(page_number)
            if self.debug_mode:
                f = self.page_table[page_number]['frame']
                print(f"Read hit: page {page_number} in frame {f}")
            return

        # miss
        self.page_faults += 1
        self.disk_reads += 1

        if len(self.frame_list) < self.frames:
            # free frame
            frame_idx = len(self.frame_list)
            self.frame_list.append(page_number)
        else:
            # evict LRU
            lru_page = self.page_order.pop(0)
            frame_idx = self.page_table[lru_page]['frame']
            if self.page_table[lru_page]['dirty']:
                self.disk_writes += 1
                if self.debug_mode:
                    print(f"Writing dirty page {lru_page} to disk from frame {frame_idx}")
            del self.page_table[lru_page]
            self.frame_list[frame_idx] = page_number

        # load new page (clean on read)
        self.page_table[page_number] = {'frame': frame_idx, 'dirty': False}
        self.page_order.append(page_number)
        if self.debug_mode:
            print(f"Page fault: loaded page {page_number} into frame {frame_idx} (read)")

    def write_memory(self, page_number):
        # Handle memory write operation
        if page_number in self.page_table:
            # Page is in memory (hit), mark as dirty
            self.page_table[page_number]['dirty'] = True
            self._touch(page_number)
            if self.debug_mode:
                f = self.page_table[page_number]['frame']
                print(f"Write hit: page {page_number} in frame {f}")
            return

        # miss
        self.page_faults += 1
        self.disk_reads += 1

        if len(self.frame_list) < self.frames:
            # free frame
            frame_idx = len(self.frame_list)
            self.frame_list.append(page_number)
        else:
            # evict LRU
            lru_page = self.page_order.pop(0)
            frame_idx = self.page_table[lru_page]['frame']
            if self.page_table[lru_page]['dirty']:
                self.disk_writes += 1
                if self.debug_mode:
                    print(f"Writing dirty page {lru_page} to disk from frame {frame_idx}")
            del self.page_table[lru_page]
            self.frame_list[frame_idx] = page_number

        # load new page and mark dirty
        self.page_table[page_number] = {'frame': frame_idx, 'dirty': True}
        self.page_order.append(page_number)
        if self.debug_mode:
            print(f"Page fault: loaded page {page_number} into frame {frame_idx} (write)")

    # ---------- stats ----------
    def get_total_disk_reads(self):
        return self.disk_reads

    def get_total_disk_writes(self):
        return self.disk_writes

    def get_total_page_faults(self):
        return self.page_faults

    # ---------- helpers ----------
    def _touch(self, page_number):
        """Move page to MRU position in page_order."""
        try:
            i = self.page_order.index(page_number)
            # move to end (most recently used)
            self.page_order.pop(i)
        except ValueError:
            pass
        self.page_order.append(page_number)
