function calculateDamage(kingHP, princess1HP, princess2HP) {
  // calculates damage made based on tower hp
  return (4824 + (3052 * 2) - kingHP - princess1HP - princess2HP);
}

function replaceCardNamesByImgPath(cardNames) {
  // transforms card names to img paths for HTML src

  return cardNames.map(card => {
    const transformedCardName = card
      .toLowerCase()
      .replace(/ /g, '_') 
      .replace(/'/g, '') 
      .replace(/\[/g, '')
      .replace(/\]/g, '');

    // construct the image path
    const imgPath = `/static/images/cards/${transformedCardName}.webp`;
    return imgPath;
  });
}

function imgPathsToHtml(imgPaths) {
  // makes HTML elements out of a list of img paths
  const spans = imgPaths.map(imgPath => `<span><img src="${imgPath}" alt="Karte" class="card-width"></span>`);
  return spans.join('');
}

// Game Modes dict. for translation
const gameModes = {
  "ClassicDecks_Friendly" : "Klassikdeck-Kampf",
  "Draft_Competitive": "Dreifach-Auswahlkampf",
  "DraftMode": "Auswahlkampf",
  "Duel_1v1_Friendly": "Duell",
  "PickMode" : "Mega-Auswahlherausforderung"
};

document.addEventListener("DOMContentLoaded", function () {

  function getLastBattleTimeInDiv() {
    // gets time data of the last battle displayed in the browser
    const battleElements = document.querySelectorAll(".battle");
    if (battleElements.length === 0) {
      // no battles are displayed
      return null;
    }

    const lastBattleElement = battleElements[battleElements.length - 1];
    const timestampElement = lastBattleElement.querySelector(".timestamp");
    const lastBattleTimeInDiv = timestampElement.textContent;
    return lastBattleTimeInDiv;
  }

  function fetchNextBattles(battleTime) {
    // fetches next battles (on click on load-more button in /battles and /player/<playerTag>)

    let url;
    const playerTagElement = document.getElementById("player-tag");

    const gameModeSelection = document.getElementById("game_mode_selection").value;

    if (playerTagElement) {
      const playerTag = playerTagElement.textContent.trim();
      const enemySelection = document.getElementById("enemy_selection").value // tag like playerTag
      url = `/api/next_battles?battle-time=${encodeURIComponent(battleTime)}&` + 
            `player-tag=${encodeURIComponent(playerTag)}&` + 
            `game-mode-selection=${encodeURIComponent(gameModeSelection)}&` +
            `enemy-selection=${encodeURIComponent(enemySelection)}`;
    } else {
      url = `/api/next_battles?battle-time=${encodeURIComponent(battleTime)}&` +
            `game-mode-selection=${encodeURIComponent(gameModeSelection)}`;
    }

    return fetch(url)
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then(battles => {
        if (battles.length > 0) {
          return battles;
        } else if (battles.message && battles.message === "No more battles to fetch.") {
          console.log("No more battles to fetch");
          return null;
        }
      })
      .catch(error => {
        console.error("Error fetching new battles:", error);
        throw error;
      });
  }

  function displayNextBattles() {
    // displays next battles

    // disable load-more button and change text
    const loadButton = document.getElementById('load-button');
    loadButton.disabled = true;
    loadButton.innerText = "Lädt...";

    const contentDiv = document.getElementById("content");
    const loadMoreDiv = document.getElementById("load-more");
    const battleTime = getLastBattleTimeInDiv();

    fetchNextBattles(battleTime)
      .then(battles => {
        // remove loadMoreDiv
        contentDiv.removeChild(loadMoreDiv);

        // No more battles to fetch
        if (battles === null) {
          return;
        }

        // create a div with class battle for each battle element
        battles.forEach(battle => {
          const div = document.createElement("div");
          div.classList.add("battle");

          // format battle time
          const timeString = battle.time;
          const timeObject = new Date(timeString);
          const year = timeObject.getUTCFullYear();
          const month = (timeObject.getUTCMonth() + 1).toString().padStart(2, '0');
          const day = timeObject.getUTCDate().toString().padStart(2, '0');
          const hours = timeObject.getUTCHours().toString().padStart(2, '0');
          const minutes = timeObject.getUTCMinutes().toString().padStart(2, '0');
          const seconds = timeObject.getUTCSeconds().toString().padStart(2, '0');
          const formattedTime = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;

          // hp values
          const player1KingHP = parseFloat(battle.player1_king_hp);
          const player1Princess1HP = parseFloat(battle.player1_princess1_hp);
          const player1Princess2HP = parseFloat(battle.player1_princess2_hp);
          const player2KingHP = parseFloat(battle.player2_king_hp);
          const player2Princess1HP = parseFloat(battle.player2_princess1_hp);
          const player2Princess2HP = parseFloat(battle.player2_princess2_hp);

          // list of img paths
          const player1DeckList = JSON.parse(battle.player1_deck_string.replace(/'/g, '"'));
          const player1ImgPaths = replaceCardNamesByImgPath(player1DeckList);
          const player2DeckList = JSON.parse(battle.player2_deck_string.replace(/'/g, '"'));
          const player2ImgPaths = replaceCardNamesByImgPath(player2DeckList);

          // inside of each battle div
          const firstPart = `
          <div class="battle-metadata">
              <span class="timestamp">${formattedTime}</span>
              <span class="game-mode">${gameModes[battle.game_mode]}</span>
          </div>
          <div class="player-score">
              <span class="player-left">${battle.player1_name}</span>
              <span class="score">${battle.player1_crowns} - ${battle.player2_crowns}</span>
              <span class="player-right">${battle.player2_name}</span>
          </div>
          `;
          
          var secondPart = ``;
          if (gameModes[battle.game_mode] == "Duell") {
            const initialPart = 
              `<div class="img-row">
                  <div class="row-left">${imgPathsToHtml(player1ImgPaths.slice(0, 4))}</div>
                  <div class="row-right">${imgPathsToHtml(player2ImgPaths.slice(0, 4))}</div>
              </div>
            `;
            secondPart += initialPart;

            for(var i = 4; i <= player1ImgPaths.length; i+=4) {
              let nextPart = `
              <div class="img-row">
                  <div class="row-left">${imgPathsToHtml(player1ImgPaths.slice(i, i+4))}</div>
                  <div class="row-right">${imgPathsToHtml(player2ImgPaths.slice(i, i+4))}</div>
              </div>
            `;
              secondPart += nextPart;

              if(i == 4 || i == 12 ||i == 20) {
                secondPart += `<hr>`
              }
            }
          } else {
            secondPart = `
            <div class="img-row">
                <div class="row-left">${imgPathsToHtml(player1ImgPaths.slice(0, 4))}</div>
                <div class="row-right">${imgPathsToHtml(player2ImgPaths.slice(0, 4))}</div>
            </div>
            <div class="img-row">
                <div class="row-left">${imgPathsToHtml(player1ImgPaths.slice(-4))}</div>
                <div class="row-right">${imgPathsToHtml(player2ImgPaths.slice(-4))}</div>
            </div>
            <hr>
          `;
          }
          
          const thirdPart = `
          <div class="elixir-damage">
              <span class="elixir"><img src="/static/images/elixir_leaked.webp" alt="Verschwendetes Elixier" class="icon-width">${battle.player1_elixir_leaked}</span>
              <span class="dmg"><img src="/static/images/damage.webp" alt="Verursachter Schaden" class="icon-width"">${calculateDamage(player1KingHP, player1Princess1HP, player1Princess2HP)}</span>
              <span class="elixir"><img src="/static/images/elixir_leaked.webp" alt="Verschwendetes Elixier" class="icon-width">${battle.player2_elixir_leaked}</span>
              <span class="dmg"><img src="/static/images/damage.webp"alt="Verursachter Schaden" class="icon-width">${calculateDamage(player2KingHP, player2Princess1HP, player2Princess2HP)}</span>
          </div>
        `;

        div.innerHTML = firstPart + secondPart + thirdPart;

        // add battle div to content div
        contentDiv.appendChild(div);
        });

        // enable button, reset text, make loadMoreDiv visible
        loadButton.disabled = false;
        loadButton.innerText = "Mehr Kämpfe laden";
        contentDiv.appendChild(loadMoreDiv);
      })
      .catch(error => {
        console.error("Error fetching new battle:", error);
      });
  }

  function getLoadButton() {
    return document.getElementById("load-button");
  }

  getLoadButton().addEventListener("click", displayNextBattles);
});