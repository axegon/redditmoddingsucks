import curses
import textwrap
from typing import Any, List, Tuple

from redditmoddingsucks.moderation.base import AbstractModeration


def _init_curses():
    """Pretty self-explanatory."""
    curses.initscr()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)


class UserInterface:
    """UserInterface is a class that represents the user interface.

    Args:
        reddit (AbstractModeration): The moderation instance.
    """

    def __init__(self, reddit: AbstractModeration):
        self.reddit = reddit
        self.queue: List[Any] = []
        self.current_item = 0
        self.scroll_offset = 0
        self.width = 0
        self.height = 0
        self.k = 0
        self._reload()
        _init_curses()

    def _get_queue(self) -> List[Any]:
        """_get_queue is a method that returns the mod queue.

        Returns:
            List[Any]: The mod queue.
        """
        return list(self.reddit.fetch_mod_queue())

    def _reload(self) -> None:
        """Reloads the mod queue."""
        self.queue = self._get_queue()
        self.current_item = 0

    def __call__(self, stdscr: curses.window, *args, **kwargs) -> None:
        """Called when the class is called.

        Should be wrapped using curses.wrapper.

        Args:
            stdscr (curses.window): The curses window.
        """

        self.stdscr = stdscr
        while self.k != ord("q"):
            self.handle_loop_start()
            self.process_input()
            self._update_selected()
            self.k = stdscr.getch()

    def process_input(self) -> None:
        """Handles user input"""
        match chr(self.k):
            case "r":
                self.set_footer("Reloading mod queue...")
                self._reload()
            case "d":
                self.set_footer(
                    f"Deleting comment/post from {self.queue[self.current_item].author}"
                )
                self.queue[self.current_item].mod.remove()
                self._reload()
            case "a":
                self.set_footer(
                    f"Approving comment/post from {self.queue[self.current_item].author}"
                )
                self.queue[self.current_item].mod.approve()
                self._reload()
            case "b":
                self._handle_ban()
            case _:
                pass

    def _handle_reload(self) -> None:
        """For manually reloading the mod queue."""
        self.set_footer("Reloading mod queue...")
        self._reload()

    def set_footer(self, msg: str) -> None:
        """Sets the footer message."""
        self.stdscr.attron(curses.color_pair(3))
        self.stdscr.addstr(self.height - 1, 1, msg)
        self.stdscr.attroff(curses.color_pair(3))
        self.stdscr.refresh()

    def _update_selected(self) -> None:
        """Visual update of the selected item."""
        current_item = self.current_item + 1 if len(self.queue) > 0 else 0
        self.set_footer(
            f"'q': Exit | 'a': Approve | 'd': Delete, 'b': Ban | 'r': Reload; "
            f"{current_item}/{len(self.queue)}",
        )
        self.stdscr.refresh()

    def _handle_delete(self) -> None:
        """Handles deleting of a single comment/post."""
        self.set_footer(
            f"Deleting comment/post from {self.queue[self.current_item].author}"
        )
        self.queue[self.current_item].mod.remove()
        self._reload()

    def _handle_approve(self) -> None:
        """Handles approving of a single comment/post."""
        self.set_footer(
            f"Deleting comment/post from {self.queue[self.current_item].author}"
        )
        self.queue[self.current_item].mod.approve()
        self._reload()

    def _handle_ban(self) -> None:
        """Handles banning of a single user -> prompt the user and choose Y/n."""
        ban = self._prompt("BANHAMMER?")
        if ban:
            self.set_footer(
                f"Banning {str(self.queue[self.current_item].author)} and removing history",
            )
            self.reddit.ban(str(self.queue[self.current_item].author))
            self.queue[self.current_item].mod.remove()

    def handle_loop_start(self) -> None:
        """Renders the curses window, checks the window size and draws the menu."""
        self.stdscr.clear()
        self.height, self.width = self.stdscr.getmaxyx()
        self.draw_menu_from_items()

    def _prompt(self, msg: str) -> bool:
        """Prompts the user with a message and returns True if the user presses Y."""
        dialog_height, dialog_width = 3, 120
        start_y, start_x = (self.height - dialog_height) // 2, (
            self.width - dialog_width
        ) // 2
        dialog_win = curses.newwin(dialog_height, dialog_width, start_y, start_x)
        dialog_win.box()

        dialog_win.addstr(1, (dialog_width - len(msg)) // 2, msg + " Y/n")
        dialog_win.refresh()
        response = dialog_win.getch()
        return response == ord("Y")

    def configure_stdscr(self) -> None:
        """Configures the curses window."""
        self.stdscr.border(0)
        title = f"Mod queue for r/{self.reddit.subreddit}"
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.addstr(0, (self.width // 2) - len(title) // 2, title)
        self.stdscr.attroff(curses.color_pair(1))

    def draw_menu_from_items(self) -> None:
        """Draws the menu from the items in the mod queue."""
        self.configure_stdscr()
        if len(self.queue) == 0:
            self.stdscr.addstr(2, 2, "No items in mod queue.")
            return

        box_height = self.height - 4
        wrapped_queue, item_start_lines = self._wrap_queue_items()
        self._update_current_item()

        current_line, item_length = self._current_item_details(item_start_lines)
        self._calculate_scroll_offset(current_line, item_length, box_height)
        self._draw_items(wrapped_queue, current_line, item_length)

    def _wrap_queue_items(self) -> Tuple[List[str], List[int]]:
        """Wraps the items in the mod queue.

        Returns:
            Tuple[List[str], List[int]]: The wrapped queue and the item start lines.
        """
        wrapped_queue = []
        item_start_lines = []
        start_line = 0

        for item in self.queue:
            wrapped_text = textwrap.wrap(self.format_item(item), self.width - 4)
            wrapped_queue.extend(wrapped_text)
            item_start_lines.append(start_line)
            start_line += len(wrapped_text)

        self.max_item = len(self.queue)
        return wrapped_queue, item_start_lines

    def _update_current_item(self) -> None:
        """Updates the current item and the selected item."""
        if self.k == curses.KEY_DOWN and self.current_item < self.max_item - 1:
            self.current_item += 1
            self._update_selected()
        elif self.k == curses.KEY_UP and self.current_item > 0:
            self.current_item -= 1
            self._update_selected()

    def _current_item_details(self, item_start_lines: List[int]) -> Tuple[int, int]:
        """Returns the current item details.

        Args:
            item_start_lines (List[int]): The item start lines.

        Returns:
            Tuple[int, int]: The current line and the item length."""
        current_line = item_start_lines[self.current_item]
        item_length = len(
            textwrap.wrap(
                self.format_item(self.queue[self.current_item]), self.width - 4
            )
        )
        return current_line, item_length

    def _calculate_scroll_offset(
        self, current_line: int, item_length: int, box_height: int
    ) -> None:
        """Calculates the scroll offset.

        Args:
            current_line (int): The current line.
            item_length (int): The item length.
            box_height (int): The box height.
        """
        if current_line < self.scroll_offset:
            self.scroll_offset = current_line
        elif current_line + item_length > self.scroll_offset + box_height:
            self.scroll_offset = current_line + item_length - box_height

    def _draw_items(
        self, wrapped_queue: List[str], current_line: int, item_length: int
    ) -> None:
        """Draws the items.

        Args:
            wrapped_queue (List[str]): The wrapped queue.
            current_line (int): The current line.
            item_length (int): The item length.
        """
        for idx, line in enumerate(
            wrapped_queue[self.scroll_offset : self.scroll_offset + self.height - 4]
        ):
            y = idx + 2
            is_current_item = (
                current_line <= idx + self.scroll_offset < current_line + item_length
            )

            if is_current_item:
                self.stdscr.attron(curses.color_pair(2))
            self.stdscr.addstr(y, 2, line)
            if is_current_item:
                self.stdscr.attroff(curses.color_pair(2))

    def format_item(self, item: Any) -> str:
        """Formats the item.

        Args:
            item (Any): The item.

        Returns:
            str: The formatted item."""
        qkind = "comment" if getattr(item, "title", None) is None else "post"
        kind = f"Item Type: {qkind.upper()}".ljust(self.width)
        author = f"Author: {str(item.author)}".ljust(self.width)
        text = "Text:".ljust(self.width)
        body = item.title if qkind == "post" else item.body
        header = "*".ljust(self.width - 4, "*")
        return f"{header}\n{kind}\n{author}\n{text}\n{body}\n"
