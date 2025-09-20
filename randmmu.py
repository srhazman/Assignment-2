from mmu import MMU
import random

class RandMMU(MMU):
    def __init__(self, frames):
        # number of physical frames
        self.frames = frames
        # mapping: page -> {frame, dirty}
        self.page_table = {}
        # which page sits in each frame
        self.frame_list = [None] * frames
        # stats
        self.disk_reads = 0
        self.disk_writes = 0
        self.page_faults = 0
        # debug flag
        self.debug_mode = False

    def set_debug(self):
        self.debug_mode = True

    def reset_debug(self):
        self.debug_mode = False

    def read_memory(self, page_number):
        if page_number in self.page_table:
            # hit
            if self.debug_mode:
                frame = self.page_table[page_number]['frame']
                print(f"Read hit: page {page_number} in frame {frame}")
            return

        # miss
        self.page_faults += 1
        self.disk_reads += 1

        # free frame available?
        if None in self.frame_list:
            frame_idx = self.frame_list.index(None)
        else:
            # need to evict random page
            frame_idx = random.randrange(self.frames)
            victim = self.frame_list[frame_idx]
            victim_entry = self.page_table[victim]
            if victim_entry['dirty']:
                self.disk_writes += 1
                if self.debug_mode:
                    print(f"Evict dirty page {victim} from frame {frame_idx}")
            del self.page_table[victim]

        # load new page
        self.frame_list[frame_idx] = page_number
        self.page_table[page_number] = {'frame': frame_idx, 'dirty': False}
        if self.debug_mode:
            print(f"Page fault: loaded page {page_number} into frame {frame_idx} (read)")

    def write_memory(self, page_number):
        if page_number in self.page_table:
            # hit → mark dirty
            self.page_table[page_number]['dirty'] = True
            if self.debug_mode:
                frame = self.page_table[page_number]['frame']
                print(f"Write hit: page {page_number} in frame {frame}")
            return

        # miss
        self.page_faults += 1
        self.disk_reads += 1

        # free frame available?
        if None in self.frame_list:
            frame_idx = self.frame_list.index(None)
        else:
            # need to evict random page
            frame_idx = random.randrange(self.frames)
            victim = self.frame_list[frame_idx]
            victim_entry = self.page_table[victim]
            if victim_entry['dirty']:
                self.disk_writes += 1
                if self.debug_mode:
                    print(f"Evict dirty page {victim} from frame {frame_idx}")
            del self.page_table[victim]

        # load new page and mark dirty
        self.frame_list[frame_idx] = page_number
        self.page_table[page_number] = {'frame': frame_idx, 'dirty': True}
        if self.debug_mode:
            print(f"Page fault: loaded page {page_number} into frame {frame_idx} (write)")

    def get_total_disk_reads(self):
        return self.disk_reads

    def get_total_disk_writes(self):
        return self.disk_writes

    def get_total_page_faults(self):
        return self.page_faults
